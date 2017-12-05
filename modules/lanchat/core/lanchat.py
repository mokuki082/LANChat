import threading
from modules.lanchat.core import sysbot, encryption, peers
from modules.lanchat.network import client, heartbeat, server
from modules.lanchat.ui import render


class LANChat():
    """ A class for the central control of all components """
    def __init__(self, host, init_peers):
        """ Constructor.

        Keyword arguments:
        host -- a Host object containing host information
        peers -- a Peers object containing peer information
        """
        # Initialize user and peers
        self.host = host  # Dictionary containing user info
        self.initial_peers = init_peers  # Initial peers object
        self.peers = peers.Peers(None, host) # peers
        # Initialize server and client
        self.server = server.TCPServer(self)
        self.client = client.TCPClient(self)
        # Initialize heartbeat
        self.heartbeat = heartbeat.HeartBeat(self)
        # Initialize Renderer
        self.render = render.Render(self)
        # Initailize sysbot
        self.sysbot = sysbot.SysBot(self)
        # Initialize encryption
        self.has_encryption = encryption.CAN_ENCRYPT
        self.encrypt_mode = 'disabled'
        if self.has_encryption:
            self.e2e = encryption.Encryption(self.host)
            self.encrypt_mode = 'enabled'

    def get_host(self):
        """ Get host information """
        return self.host

    def get_peers(self):
        """ Get peers information """
        return self.peers

    def get_blocklist(self):
        """ Get a list of blocklisted peers [(ip, port), ...] """
        return self.peers.blocklist

    def run(self):
        """ Run the application. """
        # Set up
        # Merge networks
        # send a heartbeat to everyone
        for peer in self.initial_peers.get_peers():
            args = [self.host.get_port(), self.host.get_username()]
            self.client.unicast(peer, 'hb', *args)
        # Start server
        threading.Thread(target=self.server.serve, daemon=True).start()
        # Start heartbeat
        threading.Thread(target=self.heartbeat.run, daemon=True).start()
        # Start rendering
        self.render.run()

    def stahp(self):
        """ Stop the application. """
        self.server.stahp()
        self.heartbeat.stahp()
        self.render.stahp()

    def send_message(self, message):
        """ Send a message from the host account.

        Keyword arguments:
        message - message from the host
        protocol - message
        """
        if not isinstance(message, str):
            raise ValueError
        args = []
        protocol = 'msg'
        if self.encrypt_mode == 'disabled':
            self.render.add_message(self.host.get_username(), message)
            args = [self.host.get_username(), self.host.get_port(),
                    message]
        elif self.encrypt_mode == 'enabled':
            protocol = 'msgs'
            self.render.add_message('*' + self.host.get_username(), message,
                                    mode='ENCRYPTED')
            args = [message]
        self.client.broadcast(protocol, *args, blocklist=self.peers.blocklist)

    def display_message(self, username, message, mode=None):
        """ Display a message on screen.

        Keyword arguments:
        username -- whom should the message appear to be sent by
        message -- the message
        """
        if not isinstance(username, str):
            raise ValueError
        if not isinstance(message, str):
            raise ValueError
        self.render.add_message(username, message, mode=mode)

    def do_command(self, command):
        """ Process a command from the host

        Keyword arguments:
        command -- a command that starts with '/'
        """
        self.sysbot.do_command(command)

    def sys_say(self, msg):
        """ Display a message on behalf of 'SYSTEM'

        Keyword arguments:
        msg -- the message
        """
        if not isinstance(msg, str):
            raise ValueError
        self.render.add_message('SYSTEM', msg, mode='REVERSE')
