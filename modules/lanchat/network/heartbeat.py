import time


class HeartBeat():
    def __init__(self, peers):
        self.stop = False
        self.peers = peers

    def stahp(self):
        self.stop = True

    def run(self):
        while not self.stop:
            
