import socket
import threading
import time


class TCPServer():
    def __init__(self, lanchat):
        self.lanchat = lanchat
        self.stop = False
        self.socket = socket.socket()
        self.socket.bind(lanchat.get_user().get_address())

    def stop(self):
        self.stop = True

    def serve(self):
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
        while not self.stop:
            if self.threads[thread_id][1]:
                client = self.threads[thread_id][1]
                ip = self.threads[thread_id][2]
                data = str(client.recv(1024), 'utf-8')
                username, port, *message = data.split(":")
                # Add peer (if valid)
                self.lanchat.get_user().add_peer(ip, port)
                # Render received message
                message = ':'.join(message)
                self.lanchat.display_message(username, message)
                client.close()
                # Clear client
                self.threads[thread_id][1] = None
                # Clear address
                self.threads[thread_id][2] = None
            time.sleep(0.05)


class TCPClient():
    def __init__(self, lanchat):
        self.lanchat = lanchat

    def send_message(self, message):
        for peer in self.lanchat.get_user().get_peers():
            threading.Thread(target=self.send_message_worker,
                             args=(tuple(peer), message),
                             daemon=True
                             ).start()

    def send_message_worker(self, address, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(address)
                sock.sendall(bytes(message, 'utf-8'))
        except ConnectionRefusedError:
            pass
