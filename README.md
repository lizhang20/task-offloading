[中文版](https://github.com/piaoliangkb/task-offloading/blob/master/docs/README_CN.md)

# task-offloading

A simple task offloading client for HTTP requests to offload tasks to an edge server, resulting in efficient computation and low delay costs.

This client supports **flexible task interface definition**, **automatic task offloading process**,  **easy to specify task execution server**. 

Users can access interfaces defined in a flask server to get the result server returned, nevermind how tasks send to these servers or how to get results back.

## Table of Content

- [Table of Content](#table-of-content)
- [Code Structure](#code-structure)
- [Process Overview](#process-overview)
- [Install](#install)
- [Usage](#usage)
- [License](#license)

## Code Structure

`server.py` contains `Server` data structure and a base `ServerList` data structure. ServerList maintains a currently available server list used by DecisionEngine to offload tasks. Users can define their ServerList class by inheritance from the ServerList class (such as `FlaskTestServerList`), and implement class-specific methods associated with server interfaces.

`engine.py` contains the DecisionEngine class definition. It is responsible for:

- choose offloading server according to the decision algorithm

- accept tasks and submit to the thread pool

- use the thread pool to offload tasks and get the result back

- calculating throughput on local device (request_counts / throughput_time_period)

`interfaces.py` defines task-specific interfaces (such as `FlaskTestInterfaces`, `BDInterfaces`), which will be used by the flask server exposed to uses. 

`config.py` contains different configs for different applications.

Application servers:

- `app.py` is associated with `FlaskTestConfig (config.py)`, `FlaskTestServerInterfaces (interfaces.py)`, `FlaskTestServerList (server.py)`. It defines a series of simple interfaces that can be accessed by users to indicate how to use the components mentioned before and how to program using this task offloading client.

  >Serverside code is in `flask_test_example/`. Before using this offloading client, run serverside code on different servers.

- `bdcontract.py` is another application for offloading smart contract.

## Process Overview

![process overview](docs/task-offloading.png)

## Install

This project is implemented using Python 3.7, so Python 3.7 or above is required.

```
pip install -r requirements.txt
```

## Usage

### Testing a simple flask server

In `app.py`, I defined some interfaces to access remote servers, where serverside code is in folder `flask_test_example/`. So before you run this client, you need to run serverside code on different servers. See how to run in `flask_test_example/README.md`.

After this, you can configure `FlaskTestConfig.server_list` in `config.py`, ensure server list initialization using default constructor get correct servers.

Then, run this offloading client using `sudo`, default_host is `0.0.0.0`, default_port is `8899`:

```bash
sudo python3 app.py
```

Then you can access interfaces provided by this flask server, the server will call remote server to run tasks and get results back to you. Such as:

```bash
$ curl http://host:[port]/square/20
{
    "data": "400.0",
    "server": "127.0.0.1",
    "status_code": 200,
    "throughout": 0,
    "time": 8.00912618637085
}
```

Offloading details can be seen in logs of this offloading client.

## License

MIT © 2020 piaoliangkb
