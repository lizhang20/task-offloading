from queue import Queue

from flask import Flask

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
                    server_list=server_list)
# TaskQueue instance
tq = TaskQueue(task_queue=task_queue)


@app.route("/")
def hello_world():
    task = FlaskTestInterfaces.hello_world()
    ret = de.submit_task(task=task, port=FlaskTestInterfaces.default_port)
    return ret.result().text


@app.route("/square/<num>")
def square(num):
    task = FlaskTestInterfaces.get_double(num)
    ret = de.submit_task(task=task, port=FlaskTestInterfaces.default_port)
    return ret.result().text


@app.route("/getserverlists")
def get_server_lists():
    task = FlaskTestInterfaces.get_server()
    ret = de.submit_task(task, port=FlaskTestInterfaces.default_port)
    return ret.result().text

@app.route("/getallinterfaces")
def get_all_inferfaces():
    task = FlaskTestInterfaces.list_all_interfaces()
