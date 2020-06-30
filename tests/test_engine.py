import unittest
import time

from engine import DecisionEngine
from server import ServerList, Server
from config import Config


class EngineTestCase(unittest.TestCase):
    def test_engine_initialization(self):
        server_list = ServerList()
        # decision algorithm 0
        da = Config.decision_algorithm

        for key, value in da.items():
            de = DecisionEngine(decision_algorithm=key, server_list=server_list)
            self.assertEqual(de.decision_func, value)

    def test_choose_server(self):
        server_list = ServerList.specify_server_list({
            "PC": "127.0.0.1",
        })
        de = DecisionEngine(decision_algorithm="default", server_list=server_list)

        chosen_server = de.choose_server()
        self.assertEqual("PC", chosen_server.serverName)
        self.assertEqual("127.0.0.1", chosen_server.serverIP)

        chosen_server = de._choose_server_except_localhost()
        print(chosen_server)

        de.server_list.print_all_servers()
        chosen_server = de.choose_server()
        print(chosen_server)

        server_list = ServerList()
        self.assertEqual(server_list.len(), 2)
        server_list.add_ip("192.168.56.3")
        self.assertEqual(server_list.len(), 3)

        de = DecisionEngine(decision_algorithm="minimum_ping_delay", server_list=server_list,
                            consider_throughput=True)

        self.assertTrue(de.consider_throughout)
        self.assertTrue(de.server_list.contains_ip("127.0.0.1"))
        de.server_list.print_all_servers()

        # throughput larger than expected throughput
        for i in range(20):
            de.req_time_lst.append(time.time())
        chosen_server = de.choose_server()
        print(chosen_server)
        self.assertFalse(chosen_server == Server("temp", "127.0.0.1"))

        # throughput not larger than expected throughput
        time.sleep(3)
        for i in range(5):
            de.req_time_lst.append(time.time())
        chosen_server = de.choose_server()
        print(chosen_server)
        self.assertTrue(chosen_server == Server("temp", "127.0.0.1"))

        # throughput not larger than expected throughput
        time.sleep(3)
        for i in range(20):
            time.sleep(0.2)
            de.req_time_lst.append(time.time())
        chosen_server = de.choose_server()
        print(chosen_server)
        self.assertTrue(chosen_server == Server("temp", "127.0.0.1"))

    def test_submit_task(self):
        server_list = ServerList()
        de = DecisionEngine(decision_algorithm="minimum_ping_delay", server_list=server_list)

        task1 = "offloading/10"
        ret1 = de.submit_task(task1, port=5000)
        self.assertEqual("100.0", ret1.result().text)

        tasks = [f"offloading/{num}" for num in range(20, 50)]
        rets = []
        for task in tasks:
            rets.append(de.submit_task(task, port=5000))
        for i in range(20, 50):
            self.assertEqual(f"{float(i) ** 2}", rets[i - 20].result().text)

    def test_throughput(self):
        server_list = ServerList()
        de = DecisionEngine(decision_algorithm="default", server_list=server_list)

        self.assertEqual(de.default_throughput_period, Config.DEFAULT_THROUGHPUT_PERIOD)
        self.assertEqual(de.expected_throughput, Config.EXPECTED_THROUGHPUT)

        for i in range(20):
            time.sleep(0.1)
            de.req_time_lst.append(time.time())

        self.assertEqual(de.cal_throughput(), de.default_throughput_period / 0.1)

        for i in range(20):
            time.sleep(0.2)
            de.req_time_lst.append(time.time())

        self.assertEqual(de.cal_throughput(), de.default_throughput_period / 0.2)


if __name__ == '__main__':
    unittest.main()
