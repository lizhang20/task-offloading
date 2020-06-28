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

        time.sleep(3)
        chosen_server = de.choose_server()
        print(chosen_server)

        # time larger than throughput
        # throughput larger than expected throughput
        time.sleep(3)
        de.req_count = 100
        chosen_server = de.choose_server()
        print(chosen_server)

        # time no larger than throughput period
        # throughput larger than expected throughput
        time.sleep(2.9)
        de.req_count = 100
        chosen_server = de.choose_server()
        print(chosen_server)

        # sleep more than 1 sec
        # time will larger than throughput period
        # throughput larger than expected throughput
        time.sleep(1)
        chosen_server = de.choose_server()
        print(chosen_server)

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

        self.assertEqual(de.default_throughput_period, 3)
        self.assertEqual(de.expected_throughput, 20)

        time_format = "%Y-%m-%d %H:%M:%S"
        time_str = time.strftime(time_format, time.localtime(de.start_time))
        print(time_str)

        time.sleep(1)
        de.req_count = 20
        print(de.cal_throughput())

        time.sleep(4)
        de.req_count = 100
        print(de.cal_throughput())



if __name__ == '__main__':
    unittest.main()

