import socket
import threading


class TCPClient():
    """ TCP Client for LANChat """
    def __init__(self, lanchat):
        """ Constructor

        Keyword arguments:
        lanchat -- a LANChat object
        """
        self.lanchat = lanchat
        self.peers = lanchat.get_peers()

    def send(self, message, blocklist=[]):
        """ Broadcast a message to surrounding peers

        Keyword arguments:
        message -- the message
        blocklist -- Peers that message is not sent to. [(ip, port), ...]
        """
        if not isinstance(message, str):
            raise ValueError
        if not isinstance(blocklist, list):
            raise ValueError
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
        """ Sends a message to one particular peer

        Keyword arguments:
        peer -- Peer object
        message -- The message
        """
        if not isinstance(message, str):
            raise ValueError
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                if not isinstance(peer.get_port(), int):
                    raise ValueError("Error: Port has to be an integer")
                address = (peer.get_ip(), peer.get_port())
                sock.connect(address)
                sock.sendall(bytes(message, 'utf-8'))
        except ConnectionRefusedError:
            # Let heartbeat deal with this
            pass
        except TimeoutError:
            # Let heartbeat deal with this
            pass
