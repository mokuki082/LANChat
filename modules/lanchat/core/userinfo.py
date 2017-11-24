class UserInfo():
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
