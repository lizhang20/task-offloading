import unittest

from server import Server, ServerList


class ServerTestCases(unittest.TestCase):

    def test_server_info(self):
        server1 = Server("MyPC", "127.0.0.1")

        self.assertEqual(server1.__repr__(), "Server(MyPC, 127.0.0.1)")

    def test_func_availability(self):
        server1 = Server("localhost", "127.0.0.1")
        res = server1.test_availability()
        self.assertTrue(res)

        server2 = Server("google", "google.com")
        res = server2.test_availability()
        self.assertFalse(res)

        server3 = Server("invalid ip addr", "888.888.888.888")
        res = server3.test_availability()
        self.assertFalse(res)


class ServerListTestCases(unittest.TestCase):

    def test_serverlist_initialization(self):
        serverlist1 = ServerList()

        self.assertEqual(2, serverlist1.len())

        self.assertEqual("PC", serverlist1.serverList[0].serverName)
        self.assertEqual("127.0.0.1", serverlist1.serverList[0].serverIP)

        self.assertEqual("vagrant-ubuntu", serverlist1.serverList[1].serverName)
        self.assertEqual("192.168.56.2", serverlist1.serverList[1].serverIP)

    def test_print_all_servers(self):
        serverlist1 = ServerList()
        serverlist1.print_all_servers()