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

    def test_update_server_from_interface(self):
        url = "http://127.0.0.1:5000/getserverlists"
        server_list = FlaskTestServerList()

        self.assertEqual(server_list.len(), 2)

        server_list.update_server_from_interface(url=url)


if __name__ == '__main__':
    unittest.main()
