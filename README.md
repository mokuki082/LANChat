# LANChat
A terminal based chatroom for small networks

## Getting Started
### Prerequisites

This program uses the `curses` python module, which is supported for Linux and MacOS but _not_ Windows.

Sorry Windows users.

### Running the program
```
python3 main.py [host_config peers_config]
```
Note:
- `[args]` represents optional arguments.
- `127.0.0.1:8080` is used as the default address
- Messages in the current version are _unencrypted_. Please use with caution.


### Config files
#### Host Config
The __host config file__ is a _json_ file with following format:
```
{
  "ip": "127.0.0.1",    // Host ip address
  "port": 8080,         // Host port number 0-65535
  "username": null,     // Host username, default to null
  "color": null         // Unused in the current version
}
```

The __peers config file__ is a _csv_ file (with `:` as delimiters) containing addresses of your initial peers.

For example:
```
127.0.0.1:8080
127.0.0.1:8081
```

Peers will expand as your network gets bigger. Users can use the `/save_config` command
in the program to save the current network configuration.

# License
This project is licensed under Apache2.0. See [LICENSE](https://github.com/mokuki082/LANChat/blob/master/LICENSE) for more information.

# TODO
- Color code usernames according to the `color` attribute in the config file.
- End-to-end encryption
