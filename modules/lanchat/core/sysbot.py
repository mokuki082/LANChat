import os
from modules.lanchat.core import host


class SysBot():
    def __init__(self, lanchat):
        self.lanchat = lanchat
        # Load help screen
        help_text_path = os.path.join('modules', 'lanchat', 'core',
                                      'resources', 'help.txt')
        with open(help_text_path, 'r') as help_f:
            self.help_text = help_f.read()

    def say(self, msg):
        self.lanchat.sys_say(msg)

    def save_config(self, host_config, peers_config):
        self.lanchat.host.save_config(host_config)
        self.lanchat.peers.save_config(peers_config)
        sys_msg = 'Current config saved.'
        self.say(sys_msg)

    def show_peers(self):
        users = self.lanchat.peers.get_usernames()
        if len(users) == 0:
            self.say('No peers around')
        else:
            self.say("Peers: {}".format(', '.join(users)))

    def block(self, *users):
        # 0 -- success, 1 -- invalid ip/port, 2 -- invalid format
        success = [0 for _ in users]
        if len(users) > 0:
            for i, user in enumerate(users):
                user = user.split(':')
                if len(user) == 1:  # IP only
                    ip = user[0]
                    if host.check_ip(ip):
                        self.lanchat.peers.blocklist.append((ip,))
                    else:  # Invalid IP
                        success[i] = 1
                elif len(user) == 2:  # IP and port
                    ip, port = user
                    try:
                        port = int(port)
                    except ValueError: # Non-numerical port
                        success[i] = 1
                        continue
                    # check ip and port
                    if host.check_ip(ip) and host.check_port(port):
                        self.lanchat.peers.blocklist.append((ip, port))
                    else:  # Invalid IP or port
                        success[i] = 1
                else:  # Invalid string format
                    success[i] == 2
            # Pirnt out success/error messages
            usage_errors = False
            for i, user in enumerate(users):
                if success[i] == 0:  # Success
                    self.say('successfully blocked {}'.format(user))
                elif success[i] == 1:  # Failed
                    self.say('Invalid IP/port {}'.format(user))
                elif success[i] == 2:  # Usage errors
                    usage_errors = True
            if usage_errors:
                self.say('Usage: /unblock <ip>:<port> or <ip>')
        else:
            self.say('Usage: /block <ip>:<port> or <ip>')

    def unblock(self, *users):
        ''' unblock a list of users ip or ip:port pairs
        for each user, if only ip is given, removes all peers in the blocklist
        with the same ip. Otherwise, removes the peer in the blocklist with
        matching ip + port.

        Keyword arguments:
        users -- a list of strings in ip or ip:port format
        '''
        # 0 -- success, 1 -- user not found, 2 -- invalid format
        success = [0 for _ in users]
        if len(users) > 0:
            for i, user in enumerate(users):
                user = user.split(':')
                if len(user) == 1:  # (ip,) only
                    ip = user[0]
                    if not host.check_ip(ip):
                        success[i] = 2
                        continue
                    # Remove all addresses in the blocklist with this ip
                    remove_list = []
                    for addr in self.lanchat.peers.blocklist:
                        if addr[0] == ip:
                            remove_list.append(addr)
                    if len(remove_list) > 0:
                        for i in remove_list:
                            try:
                                self.lanchat.peers.blocklist.remove(i)
                            except ValueError:  # Possible race condition
                                pass
                    else:  # Nothing to remove
                        success[i] = 1
                elif len(user) == 2:  # (ip, port) pair
                    try:
                        ip, port = user
                        port = int(port)
                        if host.check_ip(ip) and host.check_port(port):
                            if (ip, port) in self.lanchat.peers.blocklist:
                                self.lanchat.peers.blocklist.remove((ip, port))
                            else:  # Ip:port not in blocklist
                                success[i] = 1
                        else:  # Invalid IP/port
                            success[i] = 2
                    except ValueError:  # Non-integer port
                        success[i] = 2
                else:  # String format incorrect
                    success[i] = 2
            # Print out success/fail messages
            usage_errors = False
            for i, user in enumerate(users):
                if success[i] == 0:  # Success
                    self.say('successfully unblocked {}'.format(user))
                elif success[i] == 1:  # Failed
                    self.say('could not find {} in the blocklist'.format(user))
                elif success[i] == 2:  # Usage errors
                    usage_errors = True
            if usage_errors:
                self.say('Usage: /unblock <ip>:<port> or <ip>')
        else:
            self.say('Usage: /unblock <ip>:<port> or <ip>')

    def encrypt(self, arg):
        if arg == 'enable':
            if self.lanchat.has_encryption:
                self.lanchat.encrypt_mode = 'enabled'
                self.say('End-to-end encryption enabled.')
            else:
                msg = 'Pycrypto not installed. Cannot encrypt messages.'
                self.say(msg)
        elif arg == 'disable':
            self.lanchat.encrypt_mode = 'disabled'
            self.say('End-to-end encryption disabled.')
        else:
            self.say('Usage: /encrypt [disable or enable]')

    def whois(self, username):
        matched = self.lanchat.peers.search_all(username=username)
        if matched:
            for peer in matched:
                sys_msg = 'User {uname}: IP: {ip}, port: {port}'
                self.say(sys_msg.format(uname=peer.username, ip=peer.ip,
                                        port=peer.port))
        else:
            self.say('No peer named {uname} was found.'.format(uname=username))

    def change_name(self, username):
        host = self.lanchat.get_host()
        try:
            host.set_username(username)
            self.say('Username successfully changed to {}'.format(username))
        except ValueError:
            self.say('Error: Username must be within 1-16 characters')

    def do_command(self, command):
        """ Turn commands into action

        Keyword arguments:
        command -- a string that starts with '/'
        """
        if not isinstance(command, str):
            raise ValueError
        if command == '/quit' or command == '/exit':
            self.say('Shutting down...')
            self.lanchat.stahp()
        elif command.startswith('/save_config'):
            args = command.split()
            if not len(args) == 3:
                self.say('Usage: /save_config <host config> <peers config>')
            else:
                self.save_config(args[1], args[2])
        elif command == '/show_peers':
            self.show_peers()
        elif command.startswith('/block'):
            users = command.split()
            self.block(*users[1:])
        elif command.startswith('/unblock'):
            users = command.split()
            self.unblock(*users[1:])
        elif command == '/help':
            self.say(self.help_text)
        elif command.startswith('/encrypt'):
            args = command.split()
            # Condition checking
            if not len(args) == 2:
                self.say('Usage: /encrypt [disable or enable]')
            else:
                arg = args[1].lower()
                self.encrypt(arg)
        elif command.startswith('/whois'):
            args = command.split()[1:]
            if args:
                self.whois(args[0])
            else:
                self.say('Usage: /whois <username>')
        elif command.startswith('/chname'):
            uname = ' '.join(command.split()[1:])
            if uname:
                self.change_name(uname)
            else:
                self.say('Usage: /chname <new username>')
        else:
            self.say('Command not found. Try /help')
