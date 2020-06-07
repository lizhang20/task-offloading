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

    def test_server_list_initialization(self):
        server_list1 = ServerList()

        self.assertEqual(2, server_list1.len())

        self.assertEqual("PC", server_list1.serverList[0].serverName)
        self.assertEqual("127.0.0.1", server_list1.serverList[0].serverIP)

        self.assertEqual("vagrant-ubuntu", server_list1.serverList[1].serverName)
        self.assertEqual("192.168.56.2", server_list1.serverList[1].serverIP)

    def test_print_all_servers(self):
        """
        Just test print function.
        """
        server_list1 = ServerList()
        server_list1.print_all_servers()

    def test_select_min_ping_server(self):
        server_list = ServerList()
        chosen_server = server_list.select_min_ping_server()

        self.assertEqual("PC", chosen_server.serverName)
        self.assertEqual("127.0.0.1", chosen_server.serverIP)

    def test_select_random_server(self):
        """
        Sometimes this test maybe fail.
        Nevermind! In this test function, chosen_server is a
        random choice from server list.
        """
        server_list = ServerList()
        chosen_server = server_list.select_random_server()

        self.assertIsInstance(chosen_server, Server)

        self.assertEqual("PC", chosen_server.serverName)
        self.assertEqual("127.0.0.1", chosen_server.serverIP)

        # self.assertEqual("vagrant-ubuntu", chosen_server.serverName)
        # self.assertEqual("192.168.56.2", chosen_server.serverIP)

    def test_specify_server_list(self):
        d = {
            "AWS": "95.69.98.253",
            "GCP": "43.56.87.99",
            "Azure": "123.123.33.44",
        }

        server_list = ServerList.specify_server_list(d)

        for i in range(3):
            print(server_list.select_random_server())

        self.assertIsInstance(server_list, ServerList)
        self.assertEqual(3, server_list.len())
