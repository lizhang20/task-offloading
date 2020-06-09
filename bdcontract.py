from queue import Queue
import json

from flask import Flask, jsonify, request
from loguru import logger

from engine import DecisionEngine, TaskInfo
from server import ServerList, BDContractServerList
from interfaces import BDInterfaces

app = Flask(__name__)
server_list = BDContractServerList()
task_queue = Queue()
# DecisionEngine instance's decision algorithm: minimum_ping_delay
# see more info in config.py
de = DecisionEngine(decision_algorithm="default",
                    task_queue=task_queue,
                    server_list=server_list,
                    max_workers=20)


# Error handler with invalid interfaces on this flask server
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error="404 Not Found"), 404


app.register_error_handler(404, resource_not_found)


@app.route("/ping")
def ping_pong():
    logger.info("Client interface ping_pong(route'/ping') has been called")
    task = BDInterfaces.ping_pong()
    ret = de.submit_task(task=task, port=BDInterfaces.default_port)
    return ret.result().text


@app.route("/listcontractprocess")
def list_contract_process():
    """
    Call this interface for specific server:
        curl http://localhost:port/listcontractprocess?server=contract.internetapi.cn
    :return:
    """
    logger.info("Client interface list_contract_process(route'/listcontractprocess') has been called")
    param = request.args.get("server")
    server_ip = param if param else None
    task = BDInterfaces.list_CProcess()
    ret = de.submit_task(task, port=BDInterfaces.default_port, ip=server_ip)
    return ret.result().text


@app.route("/listservers")
def list_servers():
    """
    List current servers in current server list.
    :return: example: {
        "data": [
            "127.0.0.1",
            "192.168.56.2"
        ]
    }
    """
    logger.info(f"Client interface list_servers(route'/listservers') has been called")
    return jsonify(data=de.server_list.convert_to_ip_list())
