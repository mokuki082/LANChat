import sys
import threading
import network
import csv

class LANChat():
    def __init__(self, username, ip, port, config_fname='config.csv'):
        self.username = username
        # Load config file
        self.config = self.load_config_file(config_fname)
        self.server = network.TCPServer((ip, port))
        self.client = network.TCPClient(username, self.config)

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
        self.stop = False
        threading.Thread(target=self.server_worker).start()
        threading.Thread(target=self.client_worker).start()

    def server_worker(self):
        self.server.serve()

    def client_worker(self):
        while not self.stop:
            message = input("{}:".format(self.username))
            self.client.send_message(message)
