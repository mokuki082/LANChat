import threading
import network
import csv
from render import Render


class LANChat():
    def __init__(self, user):
        self.user = user
        self.stop = False
        self.server = network.TCPServer(self)
        self.client = network.TCPClient(self)
        # Initialize Renderer
        self.render = Render(self)

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
