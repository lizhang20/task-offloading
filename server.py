# This is data structure for server info in this application.

from typing import NamedTuple
import random

from loguru import logger
from ping3 import ping
import requests
import json

from config import Config


class ServerInfo(NamedTuple):
    """
    This is a NamedTuple in server.availability list
    """
    available: bool
    delay: float


class Server:

    def __init__(self, name, ip):
        self.serverName: str = name
        self.serverIP: str = ip

        # self.availability use a list to represents the history
        # of this server can connect or not.
        # items are NamedTuple: ServerInfo
        self.availability: list = list()

        # logger.info(f"Create {self.__repr__()}")

    def __repr__(self):
        return f"Server({self.serverName}, {self.serverIP})"

    def test_availability(self):
        """
        Using ping command to test availability of this server,
        then add results to self.availability: list.

        :return: Bool Type: True if test success, else False.
        """
        logger.info(f"Testing server availability: {self.__repr__()}")
        # if host unknown, return False
        # if timeout, return None
        # if success, return delay in ms
        response = ping(f"{self.serverIP}", unit="ms")
        if not response:
            logger.info(f"Testing server availability failed: unknown host {self.__repr__()}")
            self.availability.append(ServerInfo(False, 0))
            return False
        elif response is None:
            logger.info(f"Testing server availability failed: timeout {self.__repr__()}")
            self.availability.append(ServerInfo(False, 0))
            return False
        else:
            logger.info(f"Testing server availability success: time {response}ms")
            self.availability.append(ServerInfo(True, response))
            return True


class ServerList:

    def __init__(self):
        """
        Initial a server list instance according to config.py by reading Config.server_list.
        """
        # self.serverList is a list contains Server instances.
        self.serverList = list()
        # read_cnt = self.read_server_list_from_config()
        self.read_server_list_from_config()
        logger.info(f"Successfully create a {self.__class__.__name__} instance using [config]")

    def read_server_list_from_config(self):
        """
        Read server_list(a dict with <serverName, serverIP> pairs) from config module.

        :return: Successfully reading server number.
        TODO: IS THIS RETURNED VALUE USELESS??
        """
        cnt = 0
        for name, ip_addr in Config.server_list.items():
            self.serverList.append(Server(name, ip_addr))
            cnt += 1
        logger.info(f"Successfully reading {cnt} server list from config file")
        return cnt

    def update_server_list_using_list(self, lst: list):
        """
        Update self.serverList with a list param.
        :return: None
        """
        logger.info(f"Update current server list using given list {lst}")
        # Remove old unavailable servers
        self.serverList = [server for server in self.serverList if server.test_availability()]
        for item in lst:
            server = Server("AddedByUser", item)
            # if this server is available, add it to self.serverList
            if server.test_availability():
                self.serverList.append(server)
        # Remove repeated items in self.serverList
        # TODO: this should be checked using ip address of server
        self.serverList = list(set(self.serverList))
        logger.info(f"Successfully update server list, current count is {self.len()})")

    def len(self):
        return len(self.serverList)

    def print_all_servers(self):
        """
        Print all server info in ServerList.
        :return: None
        """
        for server in self.serverList:
            print(server)

    def ping(self, server: Server):
        """
        Use ping3.ping() method to test ping time.
        Cause of ping3.ping() return value:
            If normal, return [delay: float] in seconds;
            If unknown host, return [False: bool];
            If timeout, return [None].
        :param server: A Server instance (ServerName, ServerIP)
        :return:
        """
        pass

    def select_min_ping_server(self):
        """
        If choose_server algorithm is "minimum ping delay",
        use this function to select server.
        :return: If found, return a Server instance, else None.
        """
        # default max is 3000.0 ms = 3 s
        min_ping: float = 3000.0
        # default min_ping_server is None, if all server is not available,
        # just return None, let calling function deal with None.
        min_ping_server: Server = None
        for server in self.serverList:
            ret = ping(server.serverIP, unit="ms")
            if isinstance(ret, float) and ret < min_ping:
                min_ping = ret
                min_ping_server = server
        return min_ping_server

    def select_random_server(self):
        """
        Using random.choice() method to select and return a random Server.
        :return: A random Server instance in self.ServerList.
        """
        return random.choice(self.serverList)

    def map_decision_func(self):
        """
        This is a map for <str, func>. Use this to get correct decision function.

        When you have new decision function, update here and config.py

        TODO: Or maybe we can use eval() to map function name to a function.

        :return: A dict with <funcName: str, func>
        """
        d = {
            "select_random_server": self.select_random_server,
            "select_min_ping_server": self.select_min_ping_server,
        }
        return d

    @classmethod
    def specify_server_list(cls, server_list: dict):
        """
        Another constructor for ServerList class, and I do not use
        __init__() method here.
        Use this method to specify server_list in a dict.
        :param server_list: A dict with <serverName, ServerIP> paris.
        :return: A ServerList instance created by this constructor.

        Or you don't need to use this classmethod, just let __init__()
        has a parameter server_list, and check whether it is None.
        If None, read server list info from config file,
        else use this parameter to initial self.serverList.
        """
        instance = cls.__new__(cls)
        instance.serverList = list()
        for serverName, serverIP in server_list.items():
            instance.serverList.append(Server(serverName, serverIP))
        logger.info(f"Successfully create a {cls.__name__} instance using [specify_server_list]")
        return instance


class FlaskTestServerList(ServerList):
    def __init__(self):
        super().__init__()

    def update_server_from_interface(self, url: str):
        """
        Use interface which server provide to get all servers.
        Server returned value format:
        {
            "data": [
                "123.123.123.123",
                "12.12.12.12",
            ]
        }
        Purpose of this function is to parse this returned value
        of specific interface and update self.serverList with new data.
        :param url: request url of my flask server to get serverList
        :return: None
        """
        r = requests.get(url)
        logger.info(f"Call remote url {url} to get server list")
        data = json.loads(r.text)["data"]
        logger.info(f"Get {len(data)} server info from remote url {url}")
        self.update_server_list_using_list(data)
