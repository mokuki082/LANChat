import csv
import socket


class PeerInfo():
    def __init__(self, username, ip, port):
        self.set_username(username)
        if not self.set_ip(ip):
            raise ValueError('Error: Invalid IP')
        if not self.set_port(port):
            raise ValueError('Error: Invalid port')

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    ''' Getters and setters '''
    def get_username(self):
        return self.username

    def get_ip(self):
        return self.ip

    def get_port(self):
        return self.port

    def get_address(self):
        return (self.ip, self.port)

    def set_username(self, username):
        if username and len(username) <= 16:
            self.username = username
            return True
        return False

    def set_ip(self, ip):
        if ip:
            try:
                socket.inet_aton(ip)
                self.ip = ip
                return True
            except socket.error:
                return False
        return False

    def set_port(self, port):
        if not isinstance(port, int):
            return False
        if port not in range(1024, 65535):
            return False
        self.port = port
        return True


class Peers():
    def __init__(self, config_fname, host):
        # List of UserInfos
        self.host = host
        self.peers = self.load_config(config_fname)

    ''' Set up (Initialization) functions '''
    def load_config(self, config_fname):
        peers = []
        with open(config_fname, 'r') as config_f:
            # config file line format: 'ip:port'
            config_reader = csv.reader(config_f, delimiter=':')
            for row in config_reader:
                if len(row) == 2:
                    try:
                        peer = PeerInfo(None, row[0], int(row[1]))
                        # If peer is duplicated
                        if peer in peers:
                            continue
                        # If peer is the same as host
                        if (peer.get_ip() == self.host.get_ip() and
                            peer.get_port() == self.host.get_port()):
                            continue
                        peers.append(peer)
                    except ValueError:
                        continue
        return peers

    ''' Basic Operations '''
    def get_peers(self):
        return self.peers

    def add(self, peer):
        # Check if peer is of correct type
        if not isinstance(peer, PeerInfo):
            return
        # Check if peer already exists
        if peer in self.peers:
            return
        # Add peer
        self.peers.append(peer)

    def remove(self, username=None, address=None):
        peers_to_del = []
        for peer in self.peers:
            if username and username == peer.get_username:
                    peers_to_del.append(peer)
                    continue
            if address:
                if peer.get_ip == address[0] and peer.get_port == address[1]:
                    peers_to_del.append(peer)
        for peer in peers_to_del:
            self.peers.remove(peer)

    ''' Returns a list of usernames '''
    def get_usernames(self):
        users = []
        for peer in self.peers:
            if peer.get_username():
                users.append(peer.get_usernames)
        return self.identified_peers
