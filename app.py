from queue import Queue
import json

from flask import Flask, jsonify
from loguru import logger

from engine import DecisionEngine, TaskInfo
from server import ServerList, FlaskTestServerList
from interfaces import FlaskTestInterfaces

app = Flask(__name__)
server_list = FlaskTestServerList()
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


@app.route("/")
def hello_world():
    """
    Nothing but hello world!
    :return: {
        "data": "world"
    }
    """
    logger.info("Client interface hello_world(route'/') has been called")
    task = FlaskTestInterfaces.hello_world()
    ret = de.submit_task(task=task, port=FlaskTestInterfaces.default_port)
    return jsonify(data=ret.result().text)


@app.route("/square/<num>")
def square(num):
    """
    Get the param num squared.
    :param num: Number you want to calculate to get square.
    :return: num ** 2
    """
    logger.info(f"Client interface square(route'/square/<num>') has been called with param {num}")
    task = FlaskTestInterfaces.get_double(num)
    ret = de.submit_task(task=task, port=FlaskTestInterfaces.default_port)
    return jsonify(data=ret.result().text)


@app.route("/getserverlists")
def get_server_lists():
    """
    Get server list from remote interface.
    :return: example: {
        "data": [
            "127.0.0.1",
            "192.168.56.2"
        ]
    }
    """
    logger.info("Client interface getserverlists(route'/getserverlists') has been called")
    task = FlaskTestInterfaces.get_server()
    ret = de.submit_task(task, port=FlaskTestInterfaces.default_port)
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


@app.route("/updateservers")
def update_servers_from_remote():
    """
    Get server list from remote by calling FlaskTestInterfaces.get_server(),
    and update de.serverList.
    :return:
    """
    logger.info(f"Starting update local servers from remote server lists")
    # Submit a task to threadPool for getting server list.
    task = FlaskTestInterfaces.get_server()
    ret = de.submit_task(task, port=FlaskTestInterfaces.default_port)
    ret_json = json.loads(ret.result().text)
    de.server_list.update_server_list_using_list(ret_json["data"])
    return jsonify(data=de.server_list.convert_to_ip_list())
