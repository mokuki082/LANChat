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

    def unicast(self, peer, protocol, *args):
        self.send_worker(peer, protocol, *args)

    def broadcast(self, protocol, *args, blocklist=[]):
        """ Broadcast a message to surrounding peers

        Keyword arguments:
        protocol -- the protocol used for this message
        *args -- the arguments needed for the protocol
        blocklist -- a list of peers to block (optional)
        """
        if not isinstance(protocol, str):
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
                                 args=(peer, protocol, *args),
                                 daemon=True
                                 ).start()

    def construct_protocol(self, protocol, *args, receiver=None):
        """ Construct a string according to the protocol

        Keyword arguments:
        protocol -- the protocol
        args -- arguments needed for the protocol
        receiver -- peer receiving this message (optional)
        """
        if not isinstance(protocol, str):
            raise ValueError
        if protocol == 'msg':  # Message
            protocol = "msg:{port}:{user}:{message}"
            return protocol.format(port=args[0], user=args[1], message=args[2])
        if protocol == 'msgs':  # Secure message
            if (receiver and receiver.get_pubk() and
                    self.lanchat.has_encryption):
                pubk = receiver.get_pubk()
                message = args[0]
                return self.lanchat.e2e.msgs_protocol_send(message, pubk)
            else:
                raise ValueError
        if protocol == 'hb':
            return "hb:{port}:{user}".format(port=args[0], user=args[1])
        if protocol == 're':
            protocol = 're:{port}:{nip}:{nport}:{nuser}'
            return protocol.format(port=args[0], nip=args[1],
                                   nport=args[2], nuser=args[3])
        if protocol == 'kreq':
            protocol = 'kreq:{port}'
            return protocol.format(port=args[0])
        if protocol == 'kpub':
            protocol = 'kpub:{port}:{username}:{pubkey}'
            return protocol.format(port=args[0], username=args[1],
                                   pubkey=args[2])

    def send_worker(self, peer, protocol, *args):
        """ Sends a message to one particular peer

        Keyword arguments:
        peer -- Peer object
        protocol -- the protocol
        args -- a list of arguments for the protocol
        """
        if not isinstance(protocol, str):
            raise ValueError
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                if not isinstance(peer.get_port(), int):
                    raise ValueError("Error: Port has to be an integer")
                address = (peer.get_ip(), peer.get_port())
                sock.connect(address)
                message = self.construct_protocol(protocol, *args,
                                                  receiver=peer)
                sock.sendall(bytes(message, 'utf-8'))
        except ConnectionRefusedError:
            # Let heartbeat deal with this
            pass
        except TimeoutError:
            # Let heartbeat deal with this
            pass
        except ValueError as e:
            # Receiver doesn't have a public key
            pass
        except BrokenPipeError:
            # Unknown
            pass
