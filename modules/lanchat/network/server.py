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
        for thread in self.threads:
            thread[0].join()
        self.socket.close()

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
            try:
                client, addr = self.socket.accept()
            except ConnectionAbortedError:
                break
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

    def block_peer(self, ip, port):
        """ Returns a boolean of whether to block the given ip/port or not

        Keyword Arguments:
        ip -- ip of the peer
        port -- port of the peer (optional)
        """
        if not isinstance(ip, str):
            raise ValueError('Non-string IP')
        if not isinstance(port, int):
            raise ValueError('Non-numerical port')

        blocklist = self.lanchat.get_blocklist()
        for user in blocklist:
            if len(user) == 1:  # Block all peers with this ip
                if ip == user[0]:
                    return True
            else:
                if ip == user[0] and port == user[1]:
                    return True
        return False

    def host_search(self, ip, port):
        """ If the IP is a host IP, search in the peer list with multiple IP
        addresses as specified in host.get_ip_addrs().
        Returns the IP that is used in the peers list/host list, otherwise
        None.

        Keyword Argumnets:
        ip -- ip address
        port -- port number
        """
        host = self.lanchat.get_host()
        peers = self.lanchat.get_peers()
        ip_addrs = host.get_ip_addrs()
        if ip in ip_addrs:
            # Is this ip:port in peers list?
            for ip in ip_addrs:
                p = peers.search(ip=ip, port=port)
                if p:
                    return ip
            # Is this ip:port used for this host?
            for ip in ip_addrs:
                if ip == host.get_ip() and port == host.get_port():
                    return ip
        return None

    def heartbeat(self, ip, port, username):
        """ Heartbeat protocol handler

        ip -- ip of the heartbeat sender
        port -- port of the heartbeat sender
        username -- username of the heartbeat sender
        """
        if not isinstance(port, int):
            raise ValueError('Non-numerical port')
        if not isinstance(username, str):
            raise ValueError('Non-string username')
        # Strip off spaces after username for some clients
        username = username.strip()
        # check if this is a new user
        p = self.lanchat.get_peers()
        host_search_result = self.host_search(ip, port)
        ip = ip if not host_search_result else host_search_result
        found_peer = p.search(ip=ip, port=port)
        if found_peer:  # Old user
            # update last_seen
            found_peer.last_seen = datetime.now()
            # update username
            old = found_peer.get_username()
            if not (old == username):
                try:
                    old = found_peer.get_username()
                    new = username
                    found_peer.set_username(username)
                    if self.lanchat.has_encryption:
                        host = self.lanchat.get_host()
                        args = [host.get_port()]
                        peer = p.search(ip=ip, port=port)
                        self.lanchat.client.unicast(found_peer, 'kreq', *args)
                    # Display message if user was merged from
                    # another network
                    if old and not self.block_peer(ip, port):
                        sys_msg = "{} is now {}".format(old, new)
                        self.lanchat.sys_say(sys_msg)
                except ValueError:  # Invalid username
                    return
        else:  # New user
            # Add the user into peers
            try:
                new_peer = peers.PeerInfo(username, ip, port)
                p.add(new_peer)
            except ValueError:
                return
            host = self.lanchat.get_host()
            # Relay the new user to everyone in the network
            args = [host.get_port(), ip, port]
            self.lanchat.client.broadcast('re', *args,
                                          blocklist=[(ip, port)])
            if self.lanchat.has_encryption:
                args = [self.lanchat.host.get_port()]
                peer = p.search(ip=ip, port=port)
                self.lanchat.client.unicast(peer, 'kreq', *args)
            if not self.block_peer(ip, port):
                # If this ip is not in the blocklist, notify user that someone
                # has joined
                sys_msg = "{} joined the chat".format(username)
                self.lanchat.sys_say(sys_msg)

    def relay(self, from_ip, from_port, new_ip, new_port):
        if new_ip == '127.0.0.1' or new_ip == '0.0.0.0':
            new_ip = from_ip
        # check if this is a new user
        p = self.lanchat.get_peers()
        # Check if the user is host or already exists in peerlist
        host_search_result = self.host_search(new_ip, new_port)
        new_ip = new_ip if not host_search_result else host_search_result
        found_peer = p.search(ip=new_ip, port=new_port)
        if not found_peer:
            # Peer hadn't been seen before
            host = self.lanchat.get_host()
            # Send a heartbeat to the new peer
            args = [host.get_port(), host.get_username()]
            new_peer = peers.PeerInfo(None, new_ip, new_port)
            self.lanchat.client.unicast(new_peer, 'hb', *args)

    def key_request(self, ip, port):
        if not self.lanchat.has_encryption:
            return
        if not isinstance(port, int):
            raise ValueError('Non-numerical port')
        host = self.lanchat.get_host()
        pkey = self.lanchat.e2e.get_pubk()
        args = [host.get_port(), pkey]
        p = peers.PeerInfo(None, ip, port)
        self.lanchat.client.unicast(p, 'kpub', *args)

    def public_key(self, ip, port, pubk):
        # Find the peer with this public key
        p = self.lanchat.get_peers()
        found_peer = p.search(ip=ip, port=port)
        if found_peer:
            found_peer.set_pubk(pubk)

    def message(self, ip, port, message):
        if self.block_peer(ip, port):
            return
        # Check if sender is in peers
        sender = self.lanchat.get_peers().search(ip=ip, port=port)
        if sender and message:
            self.lanchat.display_message(sender.username, message)

    def message_secure(self, ip, port, ciphertext, signature):
        if self.block_peer(ip, port):
            return
        if not self.lanchat.has_encryption:
            return
        e2e = self.lanchat.e2e
        p = self.lanchat.get_peers()
        peer = p.search(ip=ip, port=port)
        if peer and peer.get_pubk():
            message = e2e.msgs_protocol_receive(ciphertext, signature,
                                                peer.get_pubk())
            if message:
                self.lanchat.display_message('*' + peer.get_username(),
                                             message,
                                             mode='ENCRYPTED')


    def handle(self, thread_id):
        """ A thread in the thread pool. Handles jobs when it sees it.

        Keyword arguments:
        thread_id -- an id that matches to its index in self.threads
        """
        while not self.stop:
            if self.threads[thread_id][1]:  # There is a job for thready!
                client, addr = self.threads[thread_id][1:]
                ip = addr[0]
                ip = ip if not ip.startswith('127.') else '127.0.0.1'
                data = str(client.recv(3072), 'utf-8')
                self.threads[thread_id][1].close()
                command, *args = data.split(':')
                # Process Command
                if command == 'msg':  # A new message from someone
                    try:
                        port, *message = args
                        port, message = int(port), ':'.join(message)
                        self.message(ip, port, message)
                    except ValueError:
                        self.thread_clr(thread_id)
                        continue

                elif command == 'msgs':  # A new encrypted message from someone
                    try:
                        port, ciphertext, signature = args
                        port = int(port)
                        self.message_secure(ip, port, ciphertext, signature)
                    except ValueError as e:
                        self.thread_clr(thread_id)
                        continue

                elif command == 'hb':  # heartbeat
                    try:
                        port, username = args
                        port = int(port)
                        self.heartbeat(ip, port, username)
                    except ValueError:
                        self.thread_clr(thread_id)
                        continue

                elif command == 're':  # Relay
                    try:
                        from_port, new_ip, new_port = args
                        from_port, new_port = int(from_port), int(new_port)
                        self.relay(ip, from_port, new_ip, new_port)
                    except ValueError:
                        self.thread_clr(thread_id)
                        continue

                elif command == 'kpub':  # Receives a public key from a peer
                    try:
                        port, pubk = args
                        port = int(port)
                        self.public_key(ip, port, pubk)
                    except ValueError:
                        self.thread_clr(thread_id)
                        continue

                elif command == 'kreq':  # A request for a public key
                    try:
                        port = args[0]
                        port = int(port)
                        self.key_request(ip, port)
                    except ValueError:
                        pass
                self.thread_clr(thread_id)
            time.sleep(0.05)

    def thread_clr(self, thread_id):
        # Clear client
        self.threads[thread_id][1] = None
        # Clear address
        self.threads[thread_id][2] = None
