import time
from datetime import datetime


class HeartBeat():
    def __init__(self, lanchat):
        self.stop = False
        self.lanchat = lanchat
        self.host = lanchat.get_host()
        self.peers = lanchat.get_peers()
        self.client = lanchat.client  # For broadcasting messages

    def stahp(self):
        self.stop = True

    def run(self):
        while not self.stop:
            # Broadcast a heartbeat to everyone
            self.client.send('hb:{}:{}'.format(self.host.get_port(),
                                               self.host.get_username()))
            # Remove all peers that hasn't been seen for more than 5 seconds
            peers_del = []
            for peer in self.peers.get_peers():
                if (peer.last_seen - datetime.now()).seconds > 5:
                    peers_del.append(peer)
            for peer in peers_del:
                if peer.username:
                    sys_msg = '{} disconnected'.format(peer.username)
                    self.lanchat.sys_say(sys_msg)
                self.peers.remove(peer)
                self.lanchat.sys_say(str(len(self.lanchat.get_peers().get_peers())))
            time.sleep(2)
