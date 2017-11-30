#!/usr/bin/env python3

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
        given_peers = peers.Peers(peer_config_fname, user)
        # If peers is empty, get a list of peers from stdin
        if not given_peers.get_peers():
            print("You haven't put in any peers in the config file!")
            print("Put down a list of 'ip port' pairs and enter a blank line when done.")
            address = input("")
            while address:
                if len(address.split()) == 2:
                    ip, port = address.split()
                    try:
                        given_peers.add(peers.PeerInfo(None, ip, int(port)))
                        print("Peer added")
                    except ValueError as e:
                        print("Given ip/port is invalid. Please try again.")
                else:
                    print("Usage: 'ip port'")
                address = input("")
            save_config = input("Would you like to save this as default config file? (y/n) ")
            if save_config == 'y':
                given_peers.save_config(os.path.join('config', 'peers.csv'))
                print('Config saved')
        # If user hasn't specified a username
        if not user.get_username():
            # Ask for user's username
            username = " " * 17
            while len(username) > 16:
                username = input("Enter a username within 16 characters: ")
            user.set_username(username)

        # Initialize LANChat API
        lanchat = lanchat.LANChat(user, given_peers)
        # Start lanchat
        lanchat.run()
        exit(0)

    except FileNotFoundError:
        print("Error: Config file not found.")
        exit(1)
    except ValueError:
        print("Error: Invalid config file")
