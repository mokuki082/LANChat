![LANChat](https://raw.githubusercontent.com/mokuki082/LANChat/master/img/logo.png)

New:
> Allow end to end encryption __if Pycrypto is installed__

## Getting Started
### Prerequisites

- __Python3__
- __Linux or MacOS__
- Pycrypto for e2e encryption. (optional)
  - To install: `pip3 install pycrypto`

### Running the program
```
./main.py [host_config peers_config]
```
Note:
- `[args]` represents optional arguments.
- `0.0.0.0:8080` is used as the default address


### Config files
__Default Config files are automatically generated when using it the first time
(with no arguments given)__

#### Host Config
The __host config file__ is a _json_ file with following format:
```
{
  "ip": "0.0.0.0",      // Host ip address
  "port": 8080,         // Host port number 0-65535
  "username": null,     // Host username, default to null
  "color": null         // Unused in the current version
}
```

The __peers config file__ contains addresses of your initial peers.

For example:
```
127.0.0.1:8080
127.0.0.1:8081
```

Peers will expand as your network gets bigger.
Users can use the `/save_config` command
in the program to save the current network configuration.

# License
This project is licensed under Apache2.0. See
[LICENSE](https://github.com/mokuki082/LANChat/blob/master/LICENSE)
for more information.
