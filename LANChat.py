import sys
import threading
import network
import csv
from render import Render

class LANChat():
    def __init__(self, username, ip, port, config_fname='config.csv'):
        self.username = username
        self.stop = False
        # Load config file
        self.config = self.load_config_file(config_fname)
        self.server = network.TCPServer((ip, port), self)
        self.client = network.TCPClient(self.config)
        # Initialize Renderer
        self.render = Render(self)

    def load_config_file(self, config_fname):
        config = []
        with open(config_fname, 'r') as f:
            config_reader = csv.reader(f, delimiter=' ')
            for row in config_reader:
                # Trust the users and no checks
                host = row[0]
                port = int(row[1])
                # Username is default to None
                config.append({'username': None, 'address': (host, port)})
        return config

    def run(self):
        # Start server
        threading.Thread(target=self.server.serve).start()
        # Start rendering
        self.render.run()

    def send_message(self, message):
        message = "{}:{}".format(self.username, message)
        self.client.send_message(message)

    def display_message(self, username, message):
        self.render.add_message(username, message)
