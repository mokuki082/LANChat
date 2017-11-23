import socket
import threading
import socketserver
import time

class TCPServer():
    def __init__(self, address):
        self.socket = socket.socket()
        self.socket.bind(address)
        self.stop = False

    def stop():
        self.stop = True

    def serve(self):
        # Create a thread pool
        nthreads = 4
        self.threads = []
        for i in range(nthreads):
            self.threads.append([threading.Thread(target=self.handle,args=(i,)),
                                None])
            self.threads[i][0].start()
        # Start listening for connections
        self.socket.listen()
        # Give a task to a thread in the thread pool
        while not self.stop:
            client, *_ = self.socket.accept()
            found_thread = False
            while not found_thread:
                for thread in self.threads:
                    if not thread[1]:
                        thread[1] = client
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
                data = str(client.recv(1024),'utf-8')
                username, *message = data.split(":")
                message = ':'.join(message)
                print("{}: {}".format(username, message))
                client.close()
                self.threads[thread_id][1] = None # Clear client
            time.sleep(0.05)



class TCPClient():
    def __init__(self, username, serverInfos):
        self.username = username
        self.serverInfos = serverInfos

    def add_serverInfo(self, serverInfo):
        self.serverInfos.append(serverInfo)

    def send_message(self, message):
        for server in self.serverInfos:
            server_addr = server["address"]
            threading.Thread(target=self.send_message_worker,
                            args=(server_addr, message)).start()

    def send_message_worker(self, address, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(address)
                message = "{}:{}".format(self.username, message)
                sock.sendall(bytes(message, 'utf-8'))
        except ConnectionRefusedError:
            pass
