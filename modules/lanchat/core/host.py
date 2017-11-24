import json
import socket


class Host():
    def __init__(self, config_fname):
        # Dictionary containing user information
        self.host = self.load_config(config_fname)

    ''' Getters and setters '''
    def get_host(self):
        return self.host

    def set_host(self, host):
        # Check validity
        if not isinstance(host, dict):
            return False
        if 'ip' not in host:
            return False
        if 'port' not in host:
            return False
        if not self.check_port(host['port']):
            return False
        if 'username' not in host:
            return False
        if not host['username']:
            return False
        if 'color' not in host:
            return False
        self.host = host
        return True

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
            return True
        return False

    def get_color(self):
        return self.host['color']

    def load_config(self, config_fname):
        with open(config_fname, 'r') as config_f:
            config = json.load(config_f)
            attr = ['username','ip','port','color']
            for i in attr:
                if i not in config:
                    raise ValueError
            if self.check_ip(config['ip']) and self.check_port(config['port']):
                return config
        raise ValueError

    ''' Validity checking functions '''

    def check_ip(self, ip):
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False

    def check_port(self, port):
        if not isinstance(port, int):
            return False
        if port not in range(1024, 65535):
            return False
        return True

    ''' Other class functions '''
    def save_config(self, config_fname):
        with open(config_fname, 'w') as f:
            content = json.dumps(self.host, sort_keys=True, indent=4)
            f.write(content)
