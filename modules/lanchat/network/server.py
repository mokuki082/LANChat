from modules.lanchat.core import peers
from datetime import datetime
import socket
import threading
import time


class TCPServer():
    """ Server for LANChat """
    def __init__(self, lanchat):
        """ Constructor

        Keyword arguments:
        lanchat -- LanChat object
        """
        self.lanchat = lanchat
        self.stop = False
        self.socket = socket.socket()
        ip = lanchat.get_host().get_ip()
        port = lanchat.get_host().get_port()
        self.socket.bind((ip, port))

    def stahp(self):
        """ Stop the server """
        self.stop = True

    def serve(self):
        """ Start serving """
        # Create a thread pool
        nthreads = 4
        # threads format: [[thread_object, client_socket, client_ip]]
        self.threads = []
        for i in range(nthreads):
            self.threads.append([threading.Thread(target=self.handle,
                                                  args=(i,),
                                                  daemon=True
                                                  ),
                                None, None]
                                )
            self.threads[i][0].start()
        # Start listening for connections
        self.socket.listen()
        # Give a task to a thread in the thread pool
        while not self.stop:
            client, addr = self.socket.accept()
            found_thread = False
            # Select a thread to give the task to
            while not found_thread:
                for thread in self.threads:
                    if not thread[1]:
                        thread[1] = client
                        thread[2] = addr
                        found_thread = True
                        break
                time.sleep(0.01)
            time.sleep(0.05)
        for thread in self.threads:
            thread.join()

    def handle(self, thread_id):
        """ A thread in the thread pool. Handles jobs when it sees it.

        Keyword arguments:
        thread_id -- an id that matches to its index in self.threads
        """
        while not self.stop:
            if self.threads[thread_id][1]:  # There is a job for thready!
                client, addr = self.threads[thread_id][1:]
                ip = addr[0]
                data = str(client.recv(1024), 'utf-8')
                command, *args = data.split(':')
                # Process Command
                if command == 'msg':  # A new message from someone
                    username, port, *message = args
                    port, message = int(port), ':'.join(message)
                    blocklist = self.lanchat.get_blocklist()
                    # Check if sender is in blocklist
                    if (ip, port) not in blocklist:
                        # Check if sender is in list of peers
                        if self.lanchat.get_peers().search(ip=ip, port=port):
                            # Render received message
                            self.lanchat.display_message(username, message)
                elif command == 'hb':  # heartbeat
                    port, username = args
                    # check if this is a new user
                    p = self.lanchat.get_peers()
                    found_peer = p.search(ip=ip, port=int(port))
                    if found_peer:  # Old user
                        # update last_seen
                        found_peer.last_seen = datetime.now()
                        # update username
                        found_peer.username = username
                    else:  # New user'
                        # Add the user into peers
                        p.add(peers.PeerInfo(username, ip, int(port)))
                        # Relay: "sd:port:new_ip:new_port:new_username"
                        host = self.lanchat.get_host()
                        msg = 're:{}:{}:{}:{}'.format(host.get_port(),
                                                      ip, port, username)
                        self.lanchat.client.send(msg,
                                                 blocklist=[(ip, int(port))])

                        sys_msg = "{} joined the chat".format(username)
                        self.lanchat.sys_say(sys_msg)
                elif command == 're':  # Relay
                    if len(args) == 4:
                        from_port, new_ip, new_port, username = args
                        from_port, new_port = int(from_port), int(new_port)
                        # check if this is a new user
                        p = self.lanchat.get_peers()
                        found_peer = p.search(ip=new_ip, port=new_port)
                        if not found_peer:
                            # Relay again: "sd:ip:port:username"
                            msg = 're:{}:{}:{}:{}'.format(host.get_port(),
                                                          new_ip,
                                                          new_port,
                                                          username)
                            self.lanchat.client.send(msg,
                                                blocklist=[(ip, from_port),
                                                           (new_ip, new_port)])
                            # Add the new peer into peers
                            p.add(peers.PeerInfo(username, new_ip, new_port))
                            sys_msg = "{} joined the chat".format(username)
                            self.lanchat.sys_say(sys_msg)
                    else:
                        self.lanchat.sys_say(str(args))
                client.close()
                # Clear client
                self.threads[thread_id][1] = None
                # Clear address
                self.threads[thread_id][2] = None
            time.sleep(0.05)
