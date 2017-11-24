import socket
import threading


class TCPClient():
    def __init__(self, peers):
        self.peers = peers

    def send(self, message, blocklist=[]):
        for peer in self.peers.get_peers():
            if peer not in blocklist:
                threading.Thread(target=self.send_worker,
                                 args=(peer, message),
                                 daemon=True
                                 ).start()

    def send_worker(self, peer, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                address = (peer.get_ip(), peer.get_port())
                sock.connect(address)
                sock.sendall(bytes(message, 'utf-8'))
        except ConnectionRefusedError:
            pass
        except TimeoutError:
            pass
