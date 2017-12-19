import csv
import socket
import os
from datetime import datetime
import errno


class PeerInfo():
    """ A class containing all peers' information """
    def __init__(self, username, ip, port, last_seen=None, pubk=None):
        """ Constructor

        Keyword arguments:
        username -- peer's username
        ip -- peer's ip
        port -- peer's port
        last_seen -- timestamp of when the peer was last seen (datetime)
        """
        self.set_username(username)
        self.set_ip(ip)
        self.set_port(port)
        self.last_seen = last_seen if last_seen else datetime.now()
        self.pubk = None

    def __str__(self):
        return 'PeerInfo({}, {}, {})'.format(self.ip, self.port, self.username)

    def get_username(self):
        """ Get username """
        return self.username

    def get_ip(self):
        """ Get IP """
        return self.ip

    def get_port(self):
        """ Get port """
        return self.port

    def get_address(self):
        """ Get (ip, port) """
        return (self.ip, self.port)

    def get_pubk(self):
        """ Get public key if exists """
        return self.pubk

    def set_username(self, username):
        """ Set username, accept None """
        if isinstance(username, str):
            if len(username) <= 16:
                self.username = username
            else:
                raise ValueError('Username too long')
        elif isinstance(username, type(None)):
            self.username = username
        else:
            raise ValueError('Invalid username type')

    def set_ip(self, ip):
        """ Set IP

        Keyword arguments:
        ip -- ip address, raises ValueError if None
        """
        if not isinstance(ip, str):
            raise ValueError('Invalid ip type')
        try:
            socket.inet_aton(ip)
            self.ip = ip
        except socket.error:
            raise ValueError('Invalid ip')

    def set_port(self, port):
        """ Set port

        Keyword arguments:
        port -- an integer between 1024-65535
        """
        if not isinstance(port, int):
            raise ValueError('Invalid port type')
        if port not in range(1024, 65535):
            raise ValueError('Invalid port range')
        self.port = port

    def set_pubk(self, pubk):
        """ Set public key

        Keyword arguments:
        pubk -- public in base64 ascii string representation
        """
        self.pubk = pubk

    def compare(self, ip, port):
        return self.ip == ip and self.port == port


class Peers():
    def __init__(self, fname, host):
        """ Constructor

        Keyword arguments:
        fname -- filename of the peers config file
        host -- Host object containing host information
        """
        # Initialize host
        self.host = host
        # Initialize block list
        self.blocklist = []  # Any ip in here cannot send to/receive from host
        if not fname:  # No filenames specified
            self.peers = []
            return
        if not isinstance(fname, str):
            raise ValueError('Invalid filename type')
        # Initialize peers
        self.load_config(fname)

    def __str__(self):
        """ String representation of the class """
        return ''.join([i.ip + ':' + str(i.port) + ',' for i in self.peers])

    def peer_is_valid(self, peer):
        # If peer is duplicated
        if self.search(ip=peer.ip, port=peer.port):
            return False
        # If peer is the same as host
        if ((peer.get_ip() == self.host.get_ip() or
                {peer.get_ip(), self.host.get_ip()} ==
                {'0.0.0.0', '127.0.0.1'}) and
                peer.port == self.host.get_port()):
            return False
        return True

    def load_config(self, fname):
        """ Load the config file and save in self.peers """
        if not isinstance(fname, str):
            raise ValueError('Invalid filename type')
        self.peers = []
        with open(fname, 'r') as config_f:
            # config file line format: 'ip:port'
            config_reader = csv.reader(config_f, delimiter=':')
            for row in config_reader:
                if not len(row):
                    continue
                if not len(row) == 2:
                    raise ValueError('Invalid config format')
                try:
                    peer = PeerInfo(None, row[0], int(row[1]))
                    if self.peer_is_valid(peer):
                        self.peers.append(peer)
                except ValueError:
                    # Invalid port or ips
                    continue

    def save_config(self, fname):
        """ Save the current peers excluding blocked peers """
        if not isinstance(fname, str):
            raise ValueError('Invalid filename type')
        # Create directories if doesn't exist
        if not os.path.exists(os.path.dirname(fname)):
            try:
                os.makedirs(os.path.dirname(fname))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(fname, 'w') as config_f:
            writer = csv.writer(config_f, delimiter=':')
            for peer in self.peers:
                ip, port = peer.get_ip(), peer.get_port()
                if (ip, port) not in self.blocklist:
                    writer.writerow([ip, port])

    def get_peers(self):
        """ Get a list of PeerInfo objects """
        return self.peers

    def add(self, peer):
        """ Add a PeerInfo object into the list """
        if self.peer_is_valid(peer):
            self.peers.append(peer)
        else:
            raise ValueError

    def remove(self, username=None, address=None):
        """ Remove all instances of peer based on given condition(s)

        Keyword arguments:
        username -- username of peer (optional)
        address -- a (ip, port) tuple (optional)
        """
        if username and not isinstance(username, str):
            raise ValueError('Invalid username type')
        if address:
            if not isinstance(address[0], str):
                raise ValueError('Invalid ip type')
            if not isinstance(address[1], int):
                raise ValueError('Invalid port type')

        peers_to_del = []
        match_cond = 2 if username and address else 1
        for peer in self.peers:
            match = 0
            if username and username == peer.get_username:
                    match += 1
                    continue
            if address:
                if peer.ip == address[0] and peer.port == address[1]:
                    match += 1
            if match == match_cond:
                peers_to_del.append(peer)
        for peer in peers_to_del:
            self.peers.remove(peer)

    def search_all(self, ip=None, port=None, username=None):
        """ Search the all peers matching all conditions given

        Keyword arguments:
        ip -- ip of the peer
        port -- port of the peer
        username -- username of the peer
        """
        if ip and not isinstance(ip, str):
            raise ValueError('Invalid ip type')
        if port and not isinstance(port, int):
            raise ValueError('Invalid port type')
        if username and not isinstance(username, str):
            raise ValueError('Invalid username type')

        match_lim = 0
        if ip:
            match_lim += 1
        if port:
            match_lim += 1
        if username:
            match_lim += 1
        matched_peers = []
        for peer in self.peers:
            match = 0
            if ip and peer.get_ip() == ip:
                match += 1
            if port and peer.get_port() == port:
                match += 1
            if username and peer.get_username() == username:
                match += 1
            if match == match_lim:
                matched_peers.append(peer)
        return matched_peers

    def search(self, ip=None, port=None, username=None):
        """ Search the first peer matching all conditions given

        Keyword arguments:
        ip -- ip of the peer
        port -- port of the peer
        username -- username of the peer
        """
        if ip and not isinstance(ip, str):
            raise ValueError('Invalid ip type')
        if port and not isinstance(port, int):
            raise ValueError('Invalid port type')
        if username and not isinstance(username, str):
            raise ValueError('Invalid username type')

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

    def get_usernames(self):
        """ Returns a list of usernames """
        users = []
        for peer in self.peers:
            if peer.get_username():
                users.append(peer.get_username())
        return users

    def block_peer(self, ip, port):
        """ Returns a boolean of whether to block the given ip/port or not

        Keyword Arguments:
        ip -- ip of the peer
        port -- port of the peer (optional)
        """
        if not isinstance(ip, str):
            raise ValueError('Non-string IP')
        if not isinstance(port, int):
            raise ValueError('Non-numerical port')

        for user in self.blocklist:
            if len(user) == 1:  # Block all peers with this ip
                if ip == user[0]:
                    return True
            else:
                if ip == user[0] and port == user[1]:
                    return True
        return False
