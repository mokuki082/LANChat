import socket
import threading


class TCPClient():
    def __init__(self, lanchat):
        self.lanchat = lanchat
        self.peers = lanchat.get_peers()

    ''' blocklist is a list of address tuples '''
    def send(self, message, blocklist=[]):
        for peer in self.peers.get_peers():
            block = False
            for ip, port in blocklist:
                if peer.compare(ip, port):
                    block = True
                    break
            if not block:
                threading.Thread(target=self.send_worker,
                                 args=(peer, message),
                                 daemon=True
                                 ).start()

    def send_worker(self, peer, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                if not isinstance(peer.get_port(), int):
                    raise ValueError("Error: Port has to be an integer")
                address = (peer.get_ip(), peer.get_port())
                sock.connect(address)
                sock.sendall(bytes(message, 'utf-8'))
        except ConnectionRefusedError:
            pass
        except TimeoutError:
            pass
