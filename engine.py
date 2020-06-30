# This is offloading decision engine.
# Purpose of this module is to determine whether some task should be offload or not.
# If so, find the most suitable server and put all data with this task to task queue.
# Task queue will send task to server and get feedback. (In another module)
# If not, execute this task on this client.

import time
import copy
import bisect
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
        # A list to store all requests timestamp. Used to calculate throughput
        # in a certain range times.
        self.req_time_lst = list()

        logger.info(
            f"Initial DecisionEngine with decision_algorithm: [{decision_algorithm}], [{max_workers}] workers, throughput period [{self.default_throughput_period}] s"
        )

    def cal_throughput(self):
        """
        Calculate throughput in a time period:
            throughput = request_count_in_a_certain_time / default_throughput_period

        All requests' timestamp is in self.req_time_lst, use bisection algorithm to
        get the index that upper than start_time. Use length of self.req_time_lst minus
        index get the request counts in this time period.

        :return: A float value of request processing per second.
        """
        cur_time = time.time()
        # Time range to calculate throughput is
        # [cur_time - self.default_throughput_period, cur_time)
        # So start_time = cur_time - DEFAULT_THROUGHPUT_PERIOD
        start_time = cur_time - self.default_throughput_period

        # Use bisection algorithm to find items in range, get the first index that
        # self.req_time_lst(index) > start_time
        # bisect.bisect_right can only deal with sorted arrays, so sorted first.
        #
        # Something wrong here is that if there is an item equals to start_time,
        # it will not be calculated. But it doesn't matters. It's to hard to
        # produce two same timestamps.
        #
        # Equals to upper_bound in C++
        # https://stackoverflow.com/questions/29471884/get-the-immediate-minimum-among-a-list-of-numbers-in-python
        # https://docs.python.org/3.6/library/bisect.html
        self.req_time_lst.sort()
        req_st_index = bisect.bisect_right(self.req_time_lst, start_time)
        throughput = len(self.req_time_lst) - req_st_index

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
            # Check if DecisionEngine can use local device to handle request.
            # In other word, check if 127.0.0.1 is in self.server_list
            logger.info("Choose server consider throughput")

            # Consider throughput on local device, if it's larger than default throughput,
            # choose server and offload requests.
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
                return Server("LocalDevice", "127.0.0.1")
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
        # Add current time to self.req_time_lst. For calculating throughput on
        # this local device future.
        # Notes that this operation is in a new thread.
        # NECESSARILY NEED A LOCK HERE???
        # I THINK NOT NECESSARY.
        cur_time = time.time()
        self.req_time_lst.append(cur_time)
        logger.info(f"Get task {data} and start offloading." +
                    f" Current time is {cur_time:.2f}, add to req_time_lst")

        # data is a TaskInfo(server: Server, task: str, port: int)
        # data = self.task_queue.get()
        server = data.server
        task = data.task
        port = data.port

        logger.info(f"Call remote server {server.serverIP}:{port} with task {task}")
        r = requests.get(f"http://{server.serverIP}:{port}/{task}")

        # r.__repr__() is "<Response [200]>"
        # r.text is the real text
        return r
