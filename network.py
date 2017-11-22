import socket, threading, socketserver

class TCPRequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self

    def handle(self):
        data = str(self.request.recv(1024),'utf-8')
        username, *message = data.split(":")
        message = ':'.join(message)
        print("{}: {}".format(username, message))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class TCPClient():
    def __init__(self, username, serverInfos):
        self.username = username
        self.serverInfos = serverInfos

    def add_serverInfo(self, serverInfo):
        self.serverInfos.append(serverInfo)

    def send_message(self, message):
        for server in self.serverInfos:
            server_addr = server["address"]
            threading.Thread(target=self.send_message_worker,
                            args=(server_addr, message)).start()

    def send_message_worker(self, address, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(address)
                message = "{}:{}".format(self.username, message)
                sock.sendall(bytes(message, 'utf-8'))
        except ConnectionRefusedError:
            pass
