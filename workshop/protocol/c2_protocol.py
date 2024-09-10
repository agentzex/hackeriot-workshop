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

    def receive_command(self):
        print("[+] Waiting for response from agent...")
        time.sleep(2)
        command_id = receive_command_id(self.socket)
        print(f"[+] Receiving response for command {command_id} ...")

        message_type, status, payload_size = struct.unpack(COMMAND_PAYLOAD_PACKET_FORMAT, self.socket.recv(6))
        if message_type != MESSAGE_RESPONSE:
            raise TypeError(f"[-] Agent sent wrong {message_type} message.")

        return status, receive_payload(self.socket, payload_size)

    # todo: #to-fill












