# This is data structure for server info in this application.

from typing import NamedTuple

from loguru import logger
from ping3 import ping

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
        Initial a server list instance according to config.py
        """
        self.serverList = list()
        read_cnt = self.read_serverlist_from_config()
        logger.info(f"Successfully reading {read_cnt} server list from config file")

    def read_serverlist_from_config(self):
        """
        Read server_list(a dict with <serverName, serverIP> pairs) from config module.

        :return: Successfully reading server number.
        """
        cnt = 0
        for name, ipaddr in Config.server_list.items():
            self.serverList.append(Server(name, ipaddr))
            cnt += 1
        return cnt

    def len(self):
        return len(self.serverList)

    def print_all_servers(self):
        """
        Print all server info in ServerList.
        :return: None
        """
        for server in self.serverList:
            print(server)




