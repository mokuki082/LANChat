import time
from datetime import datetime
from modules.lanchat.core.lanchat import LANChat


class HeartBeat():
    """ Regularly sends a hb message to peers to tell them this node
    is still alive.
    """
    def __init__(self, lanchat):
        """ Constructor

        Keyword arguments:
        lanchat -- a LANChat object
        """
        if not isinstance(lanchat, LANChat)
        self.stop = False
        self.lanchat = lanchat
        self.host = lanchat.get_host()
        self.peers = lanchat.get_peers()
        self.client = lanchat.client  # For broadcasting messages

    def stahp(self):
        """ Stop heartbeat """
        self.stop = True

    def run(self):
        """ Sends hb messages to all clients and remove peers that are
        disconnected for more than 5 seconds
        """
        while not self.stop:
            # Broadcast a heartbeat to everyone
            self.client.send('hb:{}:{}'.format(self.host.get_port(),
                                               self.host.get_username()))
            # Remove all peers that hasn't been seen for more than 4 seconds
            peers_del = []
            for peer in self.peers.get_peers():
                if int((datetime.now() - peer.last_seen).total_seconds()) > 4:
                    peers_del.append(peer)
            for peer in peers_del:
                if peer.username:
                    sys_msg = '{} disconnected'.format(peer.username)
                    self.lanchat.sys_say(sys_msg)
                self.lanchat.sys_say('Some peers disconnected')
                self.peers.remove(peer=peer)
            time.sleep(2)
