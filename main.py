from modules.lanchat.core import peers, lanchat, host
import sys
import os

if __name__ == '__main__':
    # Expecting arguments: host_config peer_config
    # Default
    host_config_fname = os.path.join('config', 'host.json')
    peer_config_fname = os.path.join('config', 'peers.csv')
    if len(sys.argv) == 3:
        _, host_config_fname, peer_config_fname = sys.argv
    else:
        print('Using default config files...')

    # Load user information from config file
    try:
        user = host.Host(host_config_fname)
        peers = peers.Peers(peer_config_fname, user)
        # If user hasn't specified a username
        if not user.get_username():
            # Ask for user's username
            username = " " * 17
            while len(username) > 16:
                username = input("Enter a username within 16 characters: ")
            user.set_username(username)

        # Initialize LANChat API
        lanchat = lanchat.LANChat(user, peers)
        # Start lanchat
        lanchat.run()
        exit(0)

    except FileNotFoundError:
        print("Error: Config file not found.")
        exit(1)
    except ValueError:
        print("Error: Invalid config file")
