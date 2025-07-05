import sys
import socket
import json
import logging
import ssl
import os
import base64

server_address = ('localhost', 8889)


def make_socket(destination_address='localhost', port=8889):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Timeout
        sock.settimeout(10)
        sock.connect((destination_address, port))
        return sock
    except Exception as ee:
        logging.warning(f"error saat membuat socket: {str(ee)}")
        return None


def send_command(command_str, is_secure=False):
    alamat_server, port_server = server_address
    sock = make_socket(alamat_server, port_server)
    if not sock:
        return ""

    logging.warning(f"Mengirim pesan:\n{command_str.splitlines()[0]}")
    try:
        sock.sendall(command_str.encode())

        response = b""

        while b"\r\n\r\n" not in response:
            chunk = sock.recv(2048)
            if not chunk:
                break
            response += chunk

        # Pisahkan header dan body
        header_part, body_part = response.split(b"\r\n\r\n", 1)
        headers = header_part.decode(errors='ignore').split("\r\n")

        content_length = 0
        for line in headers:
            if line.lower().startswith("content-length:"):
                try:
                    content_length = int(line.split(":")[1].strip())
                except (ValueError, IndexError):
                    pass
                break

        while len(body_part) < content_length:
            more_data = sock.recv(2048)
            if not more_data:
                break # Koneksi ditutup
            body_part += more_data

        return (header_part + b"\r\n\r\n" + body_part).decode(errors='ignore')

    except Exception as ee:
        logging.warning(f"Error saat menerima data: {str(ee)}")
        return ''
    finally:
        if sock:
            sock.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)

    # --- 1. GET /files (sebelum operasi) ---
    print('\n--- GET /files (sebelum operasi) ---')
    list_cmd = 'GET /files HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n'
    print(send_command(list_cmd))

    # --- 2. UPLOAD FILE donalbebek.jpg ---
    print('\n--- UPLOAD FILE donalbebek.jpg ---')
    filepath = 'donalbebek.jpg'
    if os.path.isfile(filepath):
        with open(filepath, 'rb') as f:
            filedata = f.read()
        
        filename = os.path.basename(filepath)
        filedata_b64 = base64.b64encode(filedata).decode()
        
        # Body dengan format: filename=...&data=...
        body = f'filename={filename}&data={filedata_b64}'
        content_length = len(body.encode())

        upload_request = (
            f'POST /upload HTTP/1.1\r\n'
            f'Host: localhost\r\n'
            f'Content-Length: {content_length}\r\n'
            f'Content-Type: application/x-www-form-urlencoded\r\n'
            f'Connection: close\r\n'
            f'\r\n'
            f'{body}'
        )
        print(send_command(upload_request))
    else:
        print(f'File {filepath} tidak ditemukan, upload dibatalkan.')

    # --- 3. GET /files (setelah upload) ---
    print('\n--- GET /files (setelah upload) ---')
    print(send_command(list_cmd))

    # --- 4. DELETE donalbebek.jpg ---
    print('\n--- DELETE donalbebek.jpg ---')
    delete_cmd = 'DELETE /donalbebek.jpg HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n'
    print(send_command(delete_cmd))

    # --- 5. GET /files (setelah delete) ---
    print('\n--- GET /files (setelah delete) ---')
    print(send_command(list_cmd))
