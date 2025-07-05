import sys
import socket
import json
import logging
import ssl
import os
import base64

# Ganti ke server lokal
server_address = ('localhost', 8889)


def make_socket(destination_address='localhost', port=8889):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as ee:
        logging.warning(f"error {str(ee)}")
        return None


def send_command(command_str, is_secure=False):
    alamat_server = server_address[0]
    port_server = server_address[1]
    
    sock = make_socket(alamat_server, port_server)
    if not sock:
        return False

    try:
        logging.warning(f"sending message: {command_str}")
        sock.sendall(command_str.encode())
        
        # Look for the response
        data_received = ""
        while True:
            data = sock.recv(2048)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
        
        sock.close()
        return data_received
    except Exception as ee:
        logging.warning(f"error during data receiving {str(ee)}")
        return False


def test_get_files():
    """Test GET /files"""
    cmd = "GET /files HTTP/1.1\r\nHost: localhost\r\n\r\n"
    hasil = send_command(cmd)
    print("=== GET /files ===")
    print(hasil)
    print("\n")


def test_upload_file():
    """Test POST /upload dengan file donalbebek.jpg menggunakan format sederhana"""
    try:
        with open('donalbebek.jpg', 'rb') as f:
            file_bytes = f.read()
            b64_content = base64.b64encode(file_bytes).decode('utf-8')
    except FileNotFoundError:
        # Mock content untuk testing
        mock_content = b"Mock binary content for donalbebek.jpg"
        b64_content = base64.b64encode(mock_content).decode('utf-8')
    
    # Format body: filename=nama&data=base64data
    filename = "donalbebek.jpg"
    body = f"filename={filename}&data={b64_content}"
    
    cmd = f"POST /upload HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {len(body)}\r\n\r\n{body}"
    hasil = send_command(cmd)
    print("=== POST /upload donalbebek.jpg ===")
    print(hasil)
    print("\n")


def test_delete_file():
    """Test DELETE /donalbebek.jpg"""
    cmd = "DELETE /donalbebek.jpg HTTP/1.1\r\nHost: localhost\r\n\r\n"
    hasil = send_command(cmd)
    print("=== DELETE /donalbebek.jpg ===")
    print(hasil)
    print("\n")


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    
    print("Testing HTTP Server endpoints...\n")
    
    # 1. GET /files
    test_get_files()
    
    # 2. POST /upload donalbebek.jpg
    test_upload_file()
    
    # 3. DELETE /donalbebek.jpg
    test_delete_file()
    
    # Test lagi GET /files untuk melihat perubahan
    print("=== GET /files (after operations) ===")
    test_get_files()
