import threading
from modules.lanchat.network import server, client
from modules.lanchat.ui import render


class LANChat():
    def __init__(self, user, peers):
        # Initialize user and peers
        self.user = user  # Dictionary containing user info
        self.peers = peers  # PeerInfoList
        # Initialize server and client
        self.server = server.TCPServer(self)
        self.client = client.TCPClient(self)
        # Initialize Renderer
        self.render = render.Render(self)

    def run(self):
        # Start server
        threading.Thread(target=self.server.serve, daemon=True).start()
        # Start rendering
        self.render.run()

    def send_message(self, message):
        # Message format: "username:port:message"
        message = "{}:{}:{}".format(self.user.get_username(),
                                    self.user.get_port(),
                                    message)
        self.client.send_message(message)

    def display_message(self, username, message):
        self.render.add_message(username, message)

    def get_user(self):
        return self.user

    def get_peers(self):
        return self.peers

    def do_command(self, command):
        if command == '/quit' or command == '/exit':
            # Clean up
            self.server.stahp()
            self.render.stahp()
            return
        if command.startswith('/save_config'):
            args = command.split()
            if not len(args) >= 2:
                self.sys_say('Please specify a filename.')
                return
            fname = ' '.join(args[1:])
            self.user.save_config(fname)
            self.sys_say('Current config saved in {}.'.format(fname))
            return
        if command == '/show_peers':
            users = self.peers.get_usernames()
            if len(users) == 0:
                self.sys_say('No peers around')
            else:
                self.sys_say(', '.join(users))
            return
        self.sys_say('Sowy, command not found.')

    def sys_say(self, msg):
        self.render.add_message('SYSTEM', msg)
