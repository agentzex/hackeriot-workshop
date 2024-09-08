import socket


def validate_ip(ip):
    try:
        socket.inet_aton(ip)
        # The above function will not raise an error if the address is valid
        # However, it does not check for IPv4 format completely; hence the additional split check:
        if ip.count('.') != 3 or not all(0 <= int(octet) <= 255 for octet in ip.split('.')):
            raise TypeError(f"Invalid IP address format: {ip}")
    except socket.error:
        raise TypeError(f"Invalid IP address: {ip}")


def validate_port(port):
    if not (1 <= port <= 65535):
        raise TypeError(f"Invalid port number: {port}. Port must be between 1 and 65535.")

