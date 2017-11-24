import threading
from modules.lanchat.network import server, client, heartbeat
from modules.lanchat.ui import render


class LANChat():
    def __init__(self, host, peers):
        # Initialize user and peers
        self.host = host  # Dictionary containing user info
        self.peers = peers  # PeerInfoList
        # Initialize server and client
        self.server = server.TCPServer(self)
        self.client = client.TCPClient(self)
        # Initialize heartbeat
        self.heartbeat = heartbeat.HeartBeat(self)
        # Initialize Renderer
        self.render = render.Render(self)
        # Initialize block list
        self.blocklist = []  # Any ip in here cannot send to/receive from host

    def run(self):
        # Start server
        threading.Thread(target=self.server.serve, daemon=True).start()
        threading.Thread(target=self.heartbeat.run, daemon=True).start()
        # Start rendering
        self.render.run()

    def stahp(self):
        self.server.stahp()
        self.render.stahp()

    def send_message(self, message):
        # Message format: "username:port:message"
        message = "msg:{}:{}:{}".format(self.host.get_username(),
                                    self.host.get_port(),
                                    message)
        self.client.send(message, blocklist=self.blocklist)

    def display_message(self, username, message):
        self.render.add_message(username, message)

    def get_host(self):
        return self.host

    def get_peers(self):
        return self.peers

    def get_blocklist(self):
        return self.blocklist

    def do_command(self, command):
        if command == '/quit' or command == '/exit':
            self.stahp()
            return
        if command.startswith('/save_config'):
            args = command.split()
            if not len(args) >= 2:
                self.sys_say('Please specify a filename.')
                return
            fname = ' '.join(args[1:])
            self.host.save_config(fname)
            self.sys_say('Current config saved in {}.'.format(fname))
            return
        if command == '/show_peers':
            users = self.peers.get_usernames()
            if len(users) == 0:
                self.sys_say('No peers around')
            else:
                self.sys_say(', '.join(users))
            return
        if command.startswith('/block'):
            args = command.split()
            blocked = 0
            if len(args) >= 2:
                for user in args[1:]:
                    peer = self.peers.search(username=user)
                    if peer:
                        self.blocklist.append((peer.get_ip(), peer.get_port()))
                        self.sys_say('''Blocked {}. No messages from now on will be sent to/received from this user.'''.format(user))
                    else:
                        self.sys_say("User {} not found".format(user))
            return
        if command.startswith('/unblock'):
            args = command.split()
            blocked = 0
            if len(args) >= 2:
                for user in args[1:]:
                    peer = self.peers.search(username=user)
                    if peer:
                        self.blocklist.remove((peer.get_ip(), peer.get_port()))
                        self.sys_say('Unblocked {}.'.format(user))
                    else:
                        self.sys_say("User {} not found".format(user))
            return
        self.sys_say('Sowy, command not found.')

    def sys_say(self, msg):
        self.render.add_message('SYSTEM', msg)
