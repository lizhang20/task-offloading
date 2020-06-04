# This is offloading decision engine.
# Purpose of this module is to determine whether some task should be offload or not.
# If so, find the most suitable server and put all data with this task to task queue.
# Task queue will send task to server and get feedback. (In another module)
# If not, execute this task on this client.

# Queue for task queue
from queue import Queue
from typing import NamedTuple
from concurrent.futures import ThreadPoolExecutor

from loguru import logger
import requests

from config import Config
from server import Server, ServerList


class TaskInfo(NamedTuple):
    """
    Server is just a server in ServerList, not corresponding with task.
    Port is related to specific task.
    So I add port into TaskInfo not Server.
    """
    server: Server
    task: str
    port: int


class DecisionEngine:

    def __init__(self, decision_algorithm: str, task_queue: Queue, server_list: ServerList):
        # Now decision_func is a str
        self.decision_func = Config.decision_algorithm[decision_algorithm]
        # A task queue which add tasks to
        self.task_queue = task_queue
        # Current server list
        self.server_list = server_list
        # A thread_pool to execute offloading tasks
        self.pool = ThreadPoolExecutor(10)

        logger.info(f"Initial DecisionEngine with decision_algorithm: [{decision_algorithm}]")

    def choose_server(self):
        """
        According self.decision_algorithm, this class get decision func (now this is a str)
        self.decision_func, find the best suitable server.

        :return: Server (in server.py)
        """
        # func is a decision function in ServerList class.
        func = self.server_list.map_decision_func().get(self.decision_func)
        # If there is not a server returned by decision function, func() will return None.
        chosen_server = func()
        if chosen_server is None:
            logger.info(f"Failed to choose server using {self.decision_func}")
            return None
        else:
            logger.info(f"Successfully choose server {chosen_server} using {self.decision_func}")
            return chosen_server

    def submit_task(self, task: str, port: int = 80, ip: str = None):
        """
        Add (Server, task) tuple to task queue.

        :param task: A task receive by this function. (now is a str)
        :param port: This task run on server specific port, if not specified, use 80.
        :param ip  : Server ip address where you want to run your task.
        :return: If chosen_server=self.choose_server is None, return None;
                 else result returned by Thread (a Future object).
        """
        chosen_server = Server("UserSpecific", ip) if ip else self.choose_server()
        if chosen_server is None:
            logger.info(f"Failed to submit task, chosen server is None")
            return None
        task_added = TaskInfo(chosen_server, task, port)
        logger.info(f"Successfully submit task {task_added} to ThreadPool")
        # Don't return .results() here, only you call results() method
        # it will block.
        return self.pool.submit(self.offload_task, task_added)

    def offload_task(self, data: TaskInfo):
        """
        Send task to remote server.
        Most times we use requests.get() method call some interface.

        :return: Result that remote server send back to us. Note that this is
                 response of requests.get() method. So when you print this response,
                 you will get a HTTP response code.
        """
        # data is a TaskInfo(server: Server, task: str, port: int)
        # data = self.task_queue.get()
        logger.info(f"Get task {data} and start offloading")

        server = data.server
        task = data.task
        port = data.port

        logger.info(f"Call remote server {server.serverIP}:{port} with task {task}")
        r = requests.get(f"http://{server.serverIP}:{port}/{task}")

        # r.__repr__() is "<Response [200]>"
        # r.text is the real text
        return r
