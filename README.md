# task-offloading

A simple task offloading client for HTTP requests to offload tasks to an edge server, resulting in efficient computation and low delay costs.

This client supports flexible task interface definition, automation task offloading process,  easy to specify task execution location. Users can access interfaces they defined in a flask server, by accessing them to get the right result that the server returned, nevermind how tasks send to these servers or get the result back.

## Table of Content

<!-- TOC -->

- [Table of Content](#table-of-content)
- [Code Structure](#code-structure)
- [Install](#install)

<!-- /TOC -->

## Code Structure

`server.py` contains `Server` data structure and a base `ServerList` data structure. ServerList maintains a currently available server list used by DecisionEngine to offload tasks. Users can define their ServerList class by inheritance from the ServerList class (such as `FlaskTestServerList`), and implement class-specific methods associated with server interfaces.

`engine.py` contains the DecisionEngine class definition. It is responsible for:

- choose offloading server according to the decision algorithm

- accept tasks and submit to the thread pool

- use the thread pool to offload tasks and get the result back

`interfaces.py` defines task-specific interfaces (such as `FlaskTestInterfaces`, `BDInterfaces`), which will be used by the flask server exposed to uses. 

`config.py` contains different configs for different applications.

Application servers:

- `app.py` is associated with `FlaskTestConfig (config.py)`, `FlaskTestServerInterfaces (interfaces.py)`, `FlaskTestServerList (server.py)`. It defines a series of simple interfaces that can be accessed by users to indicate how to use the components mentioned before and how to program using this task offloading client.

- `bdcontract.py` is another application for offloading smart contract.

## Install

```
pip install -r requirements.txt
```