import unittest

from server import FlaskTestServerList


class FlaskTestServerListTestCase(unittest.TestCase):
    def test_initialization(self):
        server_list = FlaskTestServerList()
        self.assertEqual(server_list.len(), 2)

        d = {
            "AWS": "95.69.98.253",
            "GCP": "43.56.87.99",
            "Azure": "123.123.33.44",
        }
        server_list1 = FlaskTestServerList.specify_server_list(d)
        self.assertEqual(len(d), server_list1.len())

    def test_update_server_from_list(self):
        server_list = FlaskTestServerList()
        new_servers = ["127.0.0.1", "127.0.0.1", "147.120.147.120"]

        server_list.update_server_list_using_list(new_servers)
        server_list.print_all_servers()


if __name__ == '__main__':
    unittest.main()
