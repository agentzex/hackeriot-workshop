import argparse
import subprocess
import datetime


def is_server_running(agent_port):
    # Use netstat or ss to check if a process is listening on agent_port
    result = subprocess.run(['netstat', '-ltnp'], capture_output=True, text=True)

    # Check if agent_port is in the result
    for line in result.stdout.splitlines():
        if f':{agent_port}' in line and 'python' in line:
            return True
    return False


def start_server(agent_port, agent_path):
    # Start the agent server
    subprocess.call(['/usr/bin/python3', agent_path, agent_port])


def parse_arguments():
    parser = argparse.ArgumentParser(description="Agent Server Monitor")
    parser.add_argument("agent_port", type=str, help="The agent's server port, that this script will monitor")
    parser.add_argument("agent_path", type=str, help="agent_server.py full path")

    args = parser.parse_args()
    return args.agent_port, args.agent_path


def get_utc_time():
    return datetime.datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S")


def main():
    agent_port, agent_path = parse_arguments()
    print(f"[+] {get_utc_time()} Checking if agent server {agent_path} running on port {agent_port}")
    if is_server_running(agent_port):
        print(f"[+] Agent server already running")
    else:
        print(f"[+] Agent server wasn't running. Trying to run now")
        start_server(agent_port, agent_path)


main()
