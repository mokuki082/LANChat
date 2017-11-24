import socket
import threading


class TCPClient():
    def __init__(self, lanchat):
        self.peers = lanchat.get_peers()

    def send_message(self, message):
        for peer in self.peers.get_peers():
            threading.Thread(target=self.send_message_worker,
                             args=(peer, message),
                             daemon=True
                             ).start()

    def send_message_worker(self, peer, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                address = (peer.get_ip(), peer.get_port())
                sock.connect(address)
                sock.sendall(bytes(message, 'utf-8'))
        except ConnectionRefusedError:
            pass
        except TimeoutError:
            pass
