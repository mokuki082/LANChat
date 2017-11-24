# LANChat
A terminal based chatroom for small networks
![](https://raw.githubusercontent.com/mokuki082/LANChat/master/screenshots/version1.0.gif)

## Getting Started
### Prerequisites
**Not supported on Windows**
This program uses the `curses` python module, which is only supported for _Linux_ and _MacOS_.
Sorry Windows users!

### Running the program
```
python3 main.py [host_config peers_config]
```
Note: `[args]` represents optional arguments.

### Config files
#### Host Config
The host config file is a json file with following format:
```
{
  "ip": "127.0.0.1", // Host ip address
  "port": 8080, // Host port number 0-65535
  "username": null, // Host username, default to null
  "color": null // Potential to specify user colors, unimplemented in current version.
}
```

The peers config fils is a csv file containing ip and ports of your initial peers.
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
