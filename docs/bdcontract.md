## 任务卸载客户端和智能合约引擎结合

该应用的用户接口代码在文件 [bdcontract.py](https://github.com/piaoliangkb/task-offloading/blob/master/bdcontract.py) 中。

和服务端关联的接口定义在文件 [interfaces.py](https://github.com/piaoliangkb/task-offloading/blob/master/interfaces.py) 中的 `BDInterfaces` 类。

### 简介

任务卸载客户端考虑了移动边缘计算环境下，移动终端计算能力不足的问题。当移动终端负载较高时，会将任务卸载到距离终端最近（延迟最低）的节点执行，并从节点获得返回结果。所以该任务卸载客户端参照本机的吞吐量（每秒请求数量）和本机与其他节点的延迟来综合考虑任务执行位置。

该客户端维护了一个智能合约可用节点的服务器列表，并将合约调用接口以 **智能合约提供的 HTTP 接口的相同格式** 提供给用户，使得使用者在使用 HTTP 接口的时候，可以轻易在原生接口调用和采用任务卸载客户端之间进行切换。

### DecisionEngine 决策引擎

决策引擎的代码位于 [engine.py](https://github.com/piaoliangkb/task-offloading/blob/master/engine.py)

决策引擎的初始化：

```python
de = DecisionEngine(decision_algorithm="minimum_ping_delay",
                    server_list=server_list,
                    max_workers=20,
                    consider_throughput=True)
```

`decision_algorithm` 参数决定了卸载过程中使用的决策函数：

- minimum_ping_delay: 在服务器列表中寻找距离当前节点延迟最低的节点进行卸载。适合边缘计算环境下对延迟的要求。

- default (random_choice): 在服务器列表中随机选取一个节点进行卸载。

`server_list` 参数为客户端维护的服务器列表。

`max_workers` 参数为决策引擎使用的线程池的最大 worker 数量。

`consider_throughput` 参数接受一个 bool 值，表示是否考虑本机的吞吐量（仅当智能合约引擎部署在本机上有效）。

向决策引擎提交任务需要使用 `de.submit_task(task, port, ip)` 方法:

其中 `task` 参数是 `interfaces.py` 文件中定义的服务端接口；`port` 参数是要请求的服务端的端口号；`ip` 字段可以指定任务卸载的具体地址，若没有该参数，则会使用当前 DecisionEngine 实例的决策函数来选择卸载地址。

返回值是一个二元组，第一个值是一个 `concurrent.futures.Future` 对象，通过 `future.result()` 方法来获得服务器返回的 response；第二个值是一个 `Server` 对象，代表卸载的目标服务器信息。

### 用户接口

