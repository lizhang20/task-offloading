import json
import time

from flask import Flask, jsonify
from loguru import logger

from engine import DecisionEngine, TaskInfo
from server import ServerList, FlaskTestServerList
from interfaces import FlaskTestInterfaces

app = Flask(__name__)
server_list = FlaskTestServerList()
# DecisionEngine instance's decision algorithm: minimum_ping_delay
# see more info in config.py
de = DecisionEngine(
    decision_algorithm="minimum_ping_delay",
    server_list=server_list,
    max_workers=20,
    consider_throughput=True
)


# Error handler with invalid interfaces on this flask server
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error="404 Not Found"), 404


app.register_error_handler(404, resource_not_found)


@app.route("/")
def hello_world():
    """
    Nothing but hello world!
    time in returned data is task offloading total delay.
    :return: {
        "data": "world",
        "time": offloading total time,
    }
    """
    logger.info("Client interface hello_world(route'/') has been called")
    # offloading start time
    st = time.time()
    task = FlaskTestInterfaces.hello_world()
    ret, server = de.submit_task(task=task, port=FlaskTestInterfaces.default_port)
    data = ret.result().text
    # get the result from offloading task, then calculate total time
    total_time = time.time() - st
    return jsonify(
        data=data, server=server, status_code=ret.result().status_code, time=total_time,
        throughput=de.cal_throughput(),
    )


@app.route("/square/<num>")
def square(num):
    """
    Get the param num squared.
    :param num: Number you want to calculate to get square.
    :return: {
        "data": num ** 2,
        "time": offloading total time,
    }
    """
    logger.info(
        f"Client interface square(route'/square/<num>') has been called with param {num}"
    )
    st = time.time()
    task = FlaskTestInterfaces.get_double(num)
    ret, server = de.submit_task(task=task, port=FlaskTestInterfaces.default_port)
    data = ret.result().text
    total_time = time.time() - st
    return jsonify(
        data=data, server=server, status_code=ret.result().status_code, time=total_time
    )


@app.route("/getserverlists")
def get_server_lists():
    """
    Get server list from remote interface.
    :return: example: {
        "data": [
            "127.0.0.1",
            "192.168.56.2"
        ],
        "time": 0.003...,
    }
    """
    logger.info(
        "Client interface getserverlists(route'/getserverlists') has been called"
    )
    st = time.time()
    task = FlaskTestInterfaces.get_server()
    ret, server = de.submit_task(task, port=FlaskTestInterfaces.default_port)
    data = ret.result().text
    total_time = time.time() - st
    data = json.loads(data)["data"]
    return jsonify(
        data=data, server=server, status_code=ret.result().status_code, time=total_time
    )


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
    :return: example: {
        "data": [
            "127.0.0.1",
            "192.168.56.2",
        ],
        "time": 0.0030...,
    }
    """
    logger.info(f"Starting update local servers from remote server lists")
    st = time.time()
    # Submit a task to threadPool for getting server list.
    task = FlaskTestInterfaces.get_server()
    ret, server = de.submit_task(task, port=FlaskTestInterfaces.default_port)
    data = ret.result().text
    total_time = time.time() - st
    ret_json = json.loads(data)
    de.server_list.update_server_list_using_list(ret_json["data"])
    return jsonify(
        data=de.server_list.convert_to_ip_list(), server=server, time=total_time
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8899)
