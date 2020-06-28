# This is offloading decision engine.
# Purpose of this module is to determine whether some task should be offload or not.
# If so, find the most suitable server and put all data with this task to task queue.
# Task queue will send task to server and get feedback. (In another module)
# If not, execute this task on this client.

import time
import copy
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
    def __init__(
        self,
        *,
        decision_algorithm: str,
        server_list: ServerList,
        max_workers: int = 20,
        consider_throughput: bool = False,
    ):
        # Now decision_func is a str
        self.decision_func = Config.decision_algorithm[decision_algorithm]
        # Current server list
        self.server_list = server_list
        # A thread_pool to execute offloading tasks
        self.pool = ThreadPoolExecutor(max_workers)

        # Something to calculate throughput
        #
        # If task offloading consider throughput on local device,
        # all fields below matters.
        self.consider_throughout = consider_throughput
        # When (end_time - start_time) > default_throughput_period,
        # calculate throughput once
        self.default_throughput_period: int = Config.DEFAULT_THROUGHPUT_PERIOD
        self.expected_throughput: int = Config.EXPECTED_THROUGHPUT
        # start_time and end_time when in this period, DecisionEngine will calculate
        # throughput per second
        self.start_time = time.time()  # start_time is instance initialization time
        self.end_time = None
        # HTTP requests count in a period
        self.req_count = 0

        logger.info(
            f"Initial DecisionEngine with decision_algorithm: [{decision_algorithm}], [{max_workers}] workers, throughput period [{self.default_throughput_period}] s"
        )

    def cal_throughput(self):
        """
        Calculate throughput in a time period:
            throughput = self.req_count / (end_time - start_time)

        :return: A float value of request processing per second.
        """
        # Test if end_time is not None
        if self.end_time is None:
            self.end_time = time.time()

        logger.info(
            f"Calculate throughput between [{self.start_time:.2f}, {self.end_time:.2f}]"
        )

        if self.req_count == 0:
            throughput = 0
        else:
            throughput = self.req_count / (self.end_time - self.start_time)

        # Reset throughput variables
        self.start_time = time.time()
        self.end_time = None
        self.req_count = 0

        return throughput

    def _choose_server_according_to_func(self, func):
        """
        Accoding to func, choose a server.
        :param func: A choose_server function in ServerList.map_decision_func().values.
        :return: A Server instance.
        """
        chosen_server = func()
        if chosen_server is None:
            logger.info(f"Failed to choose server using {self.decision_func}")
            return None
        else:
            logger.info(
                f"Successfully choose server {chosen_server} using {self.decision_func}"
            )
            return chosen_server

    def _choose_server_except_localhost(self):
        """
        I want to choose a server expect 127.0.0.1 using self.decision_func,
        so copy a new_server_list and remove 127.0.0.1,
        use the same decision func to get the server.
        :return: A Server instance.
        """
        # Make a deepcopy of self.server_list object, so remove or add items on
        # this new_server_list will not have a side effect on self.server_list.
        new_server_list = copy.deepcopy(self.server_list)
        new_server_list.remove_ip("127.0.0.1")
        if new_server_list.len() == 0:
            return None
        else:
            func = new_server_list.map_decision_func().get(self.decision_func)
            chosen_server = func()
            return chosen_server

    def choose_server(self):
        """
        According self.decision_algorithm, this class get decision func (now this is a str)
        self.decision_func, find the best suitable server.

        :return: Server (in server.py)
        """
        # func is a decision function in ServerList class.
        func = self.server_list.map_decision_func().get(self.decision_func)
        # If there is not a server returned by decision function, func() will return None.

        if self.consider_throughout and self.server_list.contains_ip("127.0.0.1"):
            # Consider throughput on local device, if it's larger than default throughput,
            # choose server and offload requests.
            logger.info("Choose server consider throughput")

            # Check if DecisionEngine can use local device to handle request.
            # In other word, check if 127.0.0.1 is in self.server_list
            if (time.time() - self.start_time) > self.default_throughput_period:
                logger.info("Compare current throughput with expected throughput...")
                if self.cal_throughput() > self.expected_throughput:
                    # Choose another server expect local device
                    logger.info(
                        "Current throughput is larger than expected throughput, "
                        + "choose an server except local device"
                    )
                    return self._choose_server_except_localhost()
                else:
                    # Run this task on local device
                    logger.info(
                        "Current throughput is not larger than expected throughput, "
                        + "choose local device as execution location"
                    )
                    return Server("local device", "127.0.0.1")
            else:
                logger.info(
                    "This time period is no larger than throughput period, "
                    + "choose local device as execution location"
                )
                # choose which server? now choose local server
                # and in this period, run tasks on local server will add self.req_count
                # when next calculate throughput, it will increase, and tasks can be
                # offloaded to other servers.
                return Server("local device", "127.0.0.1")
        else:
            # Not consider throughout on local device, using self.decision_algorithm to
            # choose server
            return self._choose_server_according_to_func(func)

    def submit_task(self, task: str, port: int = 80, ip: str = None):
        """
        Add (Server, task) tuple to task queue.

        :param task: A task receive by this function. (now is a str)
        :param port: This task run on server specific port, if not specified, use 80.
        :param ip  : Server ip address where you want to run your task.
        :return: If chosen_server=self.choose_server is None, return None;
                 else return [Future, Server.serverIP]
        """
        chosen_server = Server("UserSpecific", ip) if ip else self.choose_server()
        if chosen_server is None:
            logger.info(f"Failed to submit task, chosen server is None")
            return None
        task_added = TaskInfo(chosen_server, task, port)
        logger.info(f"Successfully submit task {task_added} to ThreadPool")
        # Don't return .results() here, only you call results() method
        # it will block.
        return self.pool.submit(self.offload_task, task_added), chosen_server.serverIP

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
