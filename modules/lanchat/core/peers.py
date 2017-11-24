import csv
import socket
from datetime import datetime


class PeerInfo():
    def __init__(self, username, ip, port, last_seen=None):
        self.username = username
        if not self.set_ip(ip):
            raise ValueError('Error: Invalid IP')
        if not self.set_port(port):
            raise ValueError('Error: Invalid port')
        if last_seen:
            self.last_seen = last_seen
        else:
            self.last_seen = datetime.now()

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

    def compare(self, ip, port):
        return self.ip == ip and self.port == port


class Peers():
    def __init__(self, config_fname, host):
        # List of UserInfos
        self.host = host
        self.peers = self.load_config(config_fname)

    def __str__(self):
        return ''.join([i.ip + ':' + str(i.port) + ',' for i in self.peers])

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
            return False
        # Add peer
        self.peers.append(peer)
        return True

    def remove(self, peer=None, username=None, address=None):
        if peer:
            self.peers.remove(peer)
            return

        peers_to_del = []
        for peer in self.peers:
            if username and username == peer.get_username:
                    peers_to_del.append(peer)
                    continue
            if address:
                if peer.ip == address[0] and peer.port == address[1]:
                    peers_to_del.append(peer)
        for peer in peers_to_del:
            self.peers.remove(peer)

    def search(self, ip=None, port=None, username=None):
        if port and not isinstance(port, int):
            raise ValueError('Error: Port has to be an integer')
        match_lim = 0
        if ip:
            match_lim += 1
        if port:
            match_lim += 1
        if username:
            match_lim += 1
        for peer in self.peers:
            match = 0
            if ip and peer.get_ip() == ip:
                match += 1
            if port and peer.get_port() == port:
                match += 1
            if username and peer.get_username() == username:
                match += 1
            if match == match_lim:
                return peer
        return None

    ''' Returns a list of usernames '''
    def get_usernames(self):
        users = []
        for peer in self.peers:
            if peer.get_username():
                users.append(peer.get_usernames)
        return self.identified_peers
