#!/usr/bin/env python3

from modules.lanchat.core import peers, lanchat, host
import sys
import os

def load_config(hostf=None, peersf=None):
    """ Loads configuration based on given filenames.
    If no filename given, default configuration is used.
    return a tuple of Host and Peers object

    Keyword arguments:
    hostf -- host config filename
    peersf -- peers config filename
    """
    # Initialize Host and Peers objects
    user = None
    given_peers = None
    if hostf:
        user = host.Host(hostf)
    else:
        user = host.Host(None)
    if peersf:
        given_peers = peers.Peers(peersf, user)
    else:
        given_peers = peers.Peers(None, user)
    return (user, given_peers)

def add_peers(given_peers):
    """ Add a list of peers from stdin

    Keyword arguments:
    given_peers -- Peers object
    """
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

if __name__ == '__main__':
    # Default file paths
    hostf = os.path.join('config', 'host.json')
    peersf = os.path.join('config', 'peers.csv')

    # Initialize user and given_peers
    user, given_peers = None, None

    # Expecting arguments: host_config peer_config
    if len(sys.argv) == 3:
        _, hostf, peersf = sys.argv
        try:
            user, given_peers = load_config(hostf=hostf, peersf=peersf)
        except ValueError:
            print("Error: Invalid configuration format.")
            exit(1)
        except FileNotFoundError:
            print("Error: Given file not found.")
            exit(1)
    else:
        try:
            user, given_peers = load_config(hostf=hostf, peersf=peersf)
            print('Using default configuration...')
        except FileNotFoundError:  # First time users
            print('Welcome to LANChat.')
            print('Generating default configuration files...')
            user, given_peers = load_config()
            # Save default settings
            user.save_config(hostf)
            print('Default host configuration saved at {}.'.format(hostf))
            given_peers.save_config(peersf)
            print('Default peers configuration saved at {}.\n'.format(peersf))

    # If peers is empty, get a list of peers from stdin
    if not given_peers.get_peers():
        # Add peers until a blank line is entered
        add_peers(given_peers)
        # Save this configuration?
        save_config = input("Would you like to save this configuration? (y/n) ")
        if save_config == 'y':
            given_peers.save_config(peersf)
            print('Config saved.')
    # If user hasn't specified a username
    if not user.get_username():
        # Ask for user's username
        username = " " * 17
        while len(username) > 16 or len(username) == 0:
            username = input("Enter a username within 1 to 16 characters: ")
        user.set_username(username)

    # Initialize LANChat API
    lanchat = lanchat.LANChat(user, given_peers)
    # Start lanchat
    lanchat.run()
    exit(0)
