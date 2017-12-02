import threading
from modules.lanchat.core import sysbot, encryption
from modules.lanchat.network import client, heartbeat, server
from modules.lanchat.ui import render


class LANChat():
    """ A class for the central control of all components """
    def __init__(self, host, peers):
        """ Constructor.

        Keyword arguments:
        host -- a Host object containing host information
        peers -- a Peers object containing peer information
        """
        # Initialize user and peers
        self.host = host  # Dictionary containing user info
        self.peers = peers  # Peers object
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
        if self.has_encryption:
            self.e2e = encryption.Encryption(self.host)

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
        for receiver in self.peers.get_peers():
            for peer in self.peers.get_peers():
                if peer is receiver:
                    continue
                args = [self.host.get_port(), peer.get_ip(),
                        peer.get_port(), 'unknown']
                self.client.unicast(receiver, 're', *args)
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

    def send_message(self, message, protocol='msg'):
        """ Send a message from the host account.

        Keyword arguments:
        message - message from the host
        protocol - message
        """
        if not isinstance(message, str):
            raise ValueError
        args = []
        if protocol == 'msg':
            args = [self.host.get_username(), self.host.get_port(),
                    message]
        elif protocol == 'msgs':
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
