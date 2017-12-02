import os


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

    def do_command(self, command):
        if not isinstance(command, str): raise ValueError
        if command == '/quit' or command == '/exit':
            self.lanchat.stahp()
            return
        if command.startswith('/save_config'):
            args = command.split()
            if not len(args) == 3:
                self.say('Usage: /save_config <host config> <peers config>')
                return
            self.lanchat.host.save_config(args[1])
            self.lanchat.peers.save_config(args[2])
            sys_msg = 'Current config saved.'.format(args[1], args[2])
            self.say(sys_msg)
            return
        if command == '/show_peers':
            users = self.lanchat.peers.get_usernames()
            if len(users) == 0:
                self.say('No peers around')
            else:
                self.say("Peers: {}".format(', '.join(users)))
            return
        if command.startswith('/block'):
            args = command.split()
            if len(args) >= 2:
                for user in args[1:]:
                    peer = self.lanchat.peers.search(username=user)
                    if peer:
                        self.lanchat.peers.blocklist.append((peer.get_ip(),
                                                     peer.get_port()))
                        sys_msg = 'User {} blocked.'
                        self.say(sys_msg.format(user))
                    else:
                        self.say("User {} not found".format(user))
            else:
                self.say("Give me the usernames that you wish to block")
            return
        if command.startswith('/unblock'):
            args = command.split()
            if len(args) >= 2:
                for user in args[1:]:
                    peer = self.lanchat.peers.search(username=user)
                    if peer:
                        blocklist = self.lanchat.peers.blocklist
                        if (peer.get_ip(), peer.get_port()) in blocklist:
                            self.lanchat.peers.blocklist.remove((peer.get_ip(),
                                                         peer.get_port()))
                            self.say('User {} unblocked'.format(user))
                        else:
                            self.say('User {} wasn\'t blocked.'.format(user))
                    else:
                        self.say("User {} not found".format(user))
            else:
                self.say("Give me the usernames that you wish to unblock")
            return
        if command == '/help':
            self.say(self.help_text)
            return
        if command.startswith('/enc '):
            message = ' '.join(command.split()[1:])
            self.lanchat.display_message(self.lanchat.host.get_username(),
                                         message)
            self.lanchat.send_message(message, protocol='msgs')
            return
        self.say('Sowy, command not found. Try /help')
