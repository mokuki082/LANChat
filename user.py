import json


class User():
    def __init__(self, config_fname='config.json'):
        self.config = self.load_config(config_fname)
        # Dictionary containing user information
        self.host = self.config['host']
        # A list of peers' [ip, port] pairs
        self.peers = self.config['peers']

    ''' Getters and setters '''
    def get_host(self):
        return self.host

    def set_host(self, host):
        # Check validity
        if not type(host) == type(dict()):
            return False
        if 'ip' not in host:
            return False
        if 'port' not in host:
            return False
        if not check_port(host['port']):
            return False
        if 'username' not in host:
            return False
        if not host['username']:
            return False
        if 'color' not in host:
            return False
        self.host = host
        return True

    def get_address(self):
        return (self.host['ip'], self.host['port'])

    def set_address(self, address):
        if self.check_address(address):
            self.host['ip'] = address[0]
            self.host['port'] = address[1]
            return True
        return False

    def get_ip(self):
        return self.host['ip']

    def set_ip(self, ip):
        if self.check_ip(ip):
            self.host['ip'] = ip
            return True
        return False

    def get_port(self):
        return self.host['port']

    def set_port(self, port):
        if self.check_port(port):
            self.host['port'] = port
            return True
        return False

    def get_username(self):
        return self.host['username']

    def set_username(self, username):
        if len(username) <= 16:
            self.host['username'] = username
            return True # Successful
        return False # Unsuccessful

    def get_color(self):
        return self.host['color']

    def get_peers(self):
        return self.peers

    def set_peers(self, peers):
        # Type checking
        if not type(peers) == type(list()):
            return False
        # Individual peer checks
        if check_peers(peers):
            self.peers = peers
            return True
        return False

    def load_config(self, config_fname):
        with open(config_fname, 'r') as config_f:
            config = json.load(config_f)
            return self.config_check(config)

    ''' Validity checking functions '''

    def check_address(self, addr):
        if not type(addr) == type(tuple()):
            return False
        if not len(addr) == 2:
            return False
        if check_ip(addr[0]) and check_port(addr[1]):
            return True
        return False

    def check_ip(ip):
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False

    def check_port(self, port):
        if not type(port) == type(int()):
            return False
        if port not in range(1024,65535):
            return False
        return True

    def config_check(self, config):
        host_ip = config['host']['ip']
        host_port = config['host']['port']
        # Check host configuration
        if not self.check_port(host_port):
            raise ValueError('Port has to be within the range 1024-65535 inclusive')
        invalid_peers = []
        for peer in config['peers']:
            # Check that port is within 1024-65535
            if not self.check_port(peer[1]):
                invalid_peers.append(peer)
            # Check that peer isn't the host (avoid loopbacks)
            if peer == [host_ip, host_port]:
                invalid_peers.append(peer)
        # Remove invalid peers
        for peer in invalid_peers:
            config['peers'].remove(peer)
        return config

    ''' Other class functions '''

    def add_peer(username, ip, port):
        # Validity checking
        if port not in range(1024, 65535):
            return
        if peer == [self.host['ip'], self.host[port]]:
            return
        if peer in self.peers:
            return
        # Add peer
        self.peers.append([ip, port])

    def save_config(config_fname):
        with open(config_fname, w) as f:
            content = json.dumps(self.config, sort_keys=True, indent=4)
            f.write(content)
