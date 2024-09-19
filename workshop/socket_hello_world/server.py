import socket


HOST = '0.0.0.0'
PORT = 9000


def init_server():
    server_msg = "Hello from server".encode()  # python sockets receive 'bytes' data type so we need to encode the string to bytes (or use b' prefix before the string)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        print("Starting Server")
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                msg = conn.recv(1024)
                if msg:
                    print(f"Received: '{msg.decode()}'")
                    conn.sendall(server_msg)


if __name__ == '__main__':
    try:
        init_server()
    except KeyboardInterrupt:
        print("[-] Exiting server")
        exit(0)