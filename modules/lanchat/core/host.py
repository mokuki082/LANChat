import json
import socket
import os
import errno

def check_ip(ip):
    """ Check that the host IP is valid

    Keyword arguments:
    ip -- a string
    """
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def check_port(port):
    """ Check that the host port is valid

    Keyword arguments:
    port -- an integer
    """
    if not isinstance(port, int):
        return False
    if port not in range(1024, 65535):
        return False
    return True

class Host():
    """ A class containing all host information. """
    def __init__(self, config_fname):
        """ Constructor

        Keyword arguments:
        config_fname -- filename of the host config file
        """
        if config_fname:
            self.load_config(config_fname)
        else:
            self.set_host({"username": None, "ip": "0.0.0.0", "port": 8080,
                           "color": None})
        # List of IP addresses associated with host
        self.ip_addr = ['0.0.0.0', '127.0.0.1']
        self.ip_addr += socket.gethostbyname_ex(socket.gethostname())[2]

    def get_ip_addrs(self):
        """ Get a list of IP addresses associated with this computer """
        return self.ip_addr

    def get_host(self):
        """ Get a dictionary containing host information. """
        return self.host

    def set_host(self, host):
        """ Set the host information.

        Keyword arguments:
        host -- A dictionary containing host information
        """
        # Check validity
        if not isinstance(host, dict):
            raise ValueError
        self.host = {}
        try:
            self.set_ip(host['ip'])
            self.set_port(host['port'])
            self.set_username(host['username'])
            self.set_color(host['color'])
        except (ValueError, KeyError):
            raise ValueError

    def get_ip(self):
        """ Get the host's IP address. """
        return self.host['ip']

    def set_ip(self, ip):
        """ Set the host's IP address.

        Keyword arguments:
        ip -- a string
        """
        # Check validity
        if not check_ip(ip):
            raise ValueError
        self.host['ip'] = ip

    def get_port(self):
        """ Get the host's port """
        return self.host['port']

    def set_port(self, port):
        """ Set the host's IP address.

        Keyword arguments:
        port -- an integer within the range 1024-65535
        """
        # Check validity
        if not check_port(port):
            raise ValueError
        self.host['port'] = port

    def get_username(self):
        """ Get the host's username. """
        return self.host['username']

    def set_username(self, username):
        """ Set the host's username.

        Keyword arguments:
        username -- a string of length not greater than 16, or None
        """
        if not isinstance(username, type(None)):
            if not isinstance(username, str):
                raise ValueError
            if not len(username) <= 16:
                raise ValueError
            self.host['username'] = username
        else:
            self.host['username'] = None

    def get_color(self):
        """ Get the host's color """
        return self.host['color']

    def set_color(self, color):
        self.host['color'] = color

    def load_config(self, config_fname):
        """ Load the config file

        Keyword arguments:
        config_fname -- host config filename
        """
        if not isinstance(config_fname, str):
            raise ValueError
        with open(config_fname, 'r') as f:
            config = json.load(f)
            self.set_host(config)

    def save_config(self, config_fname):
        """ Save the current status into a file

        Keyword arguments:
        config_fname -- filename to write to
        """
        if not isinstance(config_fname, str):
            raise ValueError
        # Create directories if doesn't exist
        if not os.path.exists(os.path.dirname(config_fname)):
            try:
                os.makedirs(os.path.dirname(config_fname))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(config_fname, 'w') as f:
            content = json.dumps(self.host, sort_keys=True, indent=4)
            f.write(content)
