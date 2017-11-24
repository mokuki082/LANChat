from LANChat import LANChat
from user import User
import sys

if __name__ == '__main__':
    # Expecting arguments: config_fname
    config_fname = 'config.json' # Default
    if len(sys.argv) >= 2:
        _, *config_fname = sys.argv
        config_fname = ''.join(config_fname)

    # Load user information from config file
    try:
        user = User(config_fname=config_fname)
    except FileNotFoundError:
        print("Error: Config file not found.")
        exit(1)

    # If user hasn't specified a username
    if not user.get_username():
        # Ask for user's username
        username = " " * 17
        while len(username) > 16:
            username = input("Enter a username within 16 characters: ")
        user.set_username(username)

    # Initialize LANChat API
    lanchat = LANChat(user)
    # Start lanchat
    lanchat.run()
    exit(0)
