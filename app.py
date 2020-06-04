from queue import Queue

from flask import Flask

from engine import DecisionEngine, TaskInfo
from server import ServerList
from taskqueue import TaskQueue
from config import Config, SmartContractConfig

app = Flask(__name__)
server_list = ServerList()
task_queue = Queue()
# DecisionEngine instance's decision algorithm: minimum_ping_delay
# see more info in config.py
de = DecisionEngine(decision_algorithm="minimum_ping_delay",
                    task_queue=task_queue,
                    server_list=server_list)
# TaskQueue instance
tq = TaskQueue(task_queue=task_queue)


@app.route("/")
def hello_world():
    return "Hello, world!"


@app.route("/square/<num>")
def square(num):
    task = f"/offloading/{num}"
    ret = de.submit_task(task, port=5000)
    return ret.result().text
