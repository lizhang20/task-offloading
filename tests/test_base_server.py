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

    def test_server_equal(self):
        server1 = Server("s1", "127.0.0.1")
        server2 = Server("s2", "127.0.0.1")
        self.assertEqual(server2, server1)
        server_set = set()
        server_set.add(server1)
        server_set.add(server2)


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

        self.assertTrue(chosen_server in server_list.serverList)

        # self.assertEqual("vagrant-ubuntu", chosen_server.serverName)
        # self.assertEqual("192.168.56.2", chosen_server.serverIP)

    def test_specify_server_list(self):
        d = {
            "AWS": "95.69.98.253",
            "GCP": "43.56.87.99",
            "Azure": "123.123.33.44",
            "AWS1": "95.69.98.253",
            "GCP1": "43.56.87.99",
            "Azure1": "123.123.33.44",
        }

        server_list = ServerList.specify_server_list(d)

        self.assertIsInstance(server_list, ServerList)
        self.assertEqual(3, server_list.len())

    def test_update_server_list(self):
        d = {
            "AWS": "95.69.98.253",
            "GCP": "43.56.87.99",
            "Azure": "123.123.33.44",
        }
        server_list = ServerList.specify_server_list(d)

        self.assertEqual(server_list.len(), len(d))

        lst = ["127.0.0.1", "128.0.0.0"]
        server_list.update_server_list_using_list(lst)

        self.assertEqual(server_list.len(), 1)
        server_list.print_all_servers()

    def test_server_list_duplicated_items(self):
        server_list = ServerList()
        self.assertEqual(server_list.len(), 2)

        added_server = ["127.0.0.1", "127.0.0.1", "192.168.56.2"]
        server_list.update_server_list_using_list(added_server)
        self.assertEqual(server_list.len(), 2)