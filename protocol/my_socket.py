

class MySocket:
    def __init__(self, s):
        self.s = s


    def send(self, data):
        # Check if the data is a string; if so, encode it to bytes
        if isinstance(data, str):
            data = data.encode()
        elif not isinstance(data, bytes):
            raise TypeError("Data must be either str or bytes")

        self.s.sendall(data)
