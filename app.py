from queue import Queue

from flask import Flask, jsonify
from loguru import logger

from engine import DecisionEngine, TaskInfo
from server import ServerList
from taskqueue import TaskQueue
from interfaces import FlaskTestInterfaces

app = Flask(__name__)
server_list = ServerList()
task_queue = Queue()
# DecisionEngine instance's decision algorithm: minimum_ping_delay
# see more info in config.py
de = DecisionEngine(decision_algorithm="default",
                    task_queue=task_queue,
                    server_list=server_list,
                    max_workers=20)
# TaskQueue instance
tq = TaskQueue(task_queue=task_queue)


# Error handler with invalid interfaces on this flask server
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error="404 Not Found"), 404


app.register_error_handler(404, resource_not_found)


@app.route("/")
def hello_world():
    logger.info("Client interface hello_world(route'/') has been called")
    task = FlaskTestInterfaces.hello_world()
    ret = de.submit_task(task=task, port=FlaskTestInterfaces.default_port)
    return jsonify(data=ret.result().text)


@app.route("/square/<num>")
def square(num):
    logger.info(f"Client interface square(route'/square/<num>') has been called with param {num}")
    task = FlaskTestInterfaces.get_double(num)
    ret = de.submit_task(task=task, port=FlaskTestInterfaces.default_port)
    return jsonify(data=ret.result().text)


@app.route("/getserverlists")
def get_server_lists():
    logger.info("Client interface getserverlists(route'/getserverlists') has been called")
    task = FlaskTestInterfaces.get_server()
    ret = de.submit_task(task, port=FlaskTestInterfaces.default_port)
    return ret.result().text
