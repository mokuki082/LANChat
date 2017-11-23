from LANChat import LANChat

if __name__ == '__main__':
    # condition checking
    if len(sys.argv) < 3:
        print("Please specify Host and Port")
        exit(0)
    if not sys.argv[2].isdigit() or int(sys.argv[2]) not in range(1024,65535):
        print("Invalid Port")
        exit(0)

    # Ask for user's username
    username = " " * 17
    while len(username) > 16:
        username = input("Enter a username within 16 characters:")

    # Start LANChat
    LANChat(username, sys.argv[1], int(sys.argv[2])).run()
