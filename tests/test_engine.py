import unittest
from queue import Queue

from engine import DecisionEngine
from server import ServerList, Server


class EngineTestCase(unittest.TestCase):
    def test_engine_initialization(self):
        q = Queue()
        server_list = ServerList()
        de1 = DecisionEngine("default", q, server_list)

        self.assertEqual(de1.decision_func, "random_choice")
        print(de1.task_queue)
        print(de1.server_list)

        de2 = DecisionEngine("bdcontract", q, server_list)
        self.assertEqual("min_ping", de2.decision_func)

    def test_choose_server(self):
        q = Queue()
        server_list = ServerList()
        de = DecisionEngine("default", q, server_list)

        chosen_server = de.choose_server()
        self.assertEqual("PC", chosen_server.serverName)
        self.assertEqual("127.0.0.1", chosen_server.serverIP)

    def test_submit_task(self):
        q = Queue()
        server_list = ServerList()
        de = DecisionEngine("default", q, server_list)

        task1 = "offloading/10"
        ret1 = de.submit_task(task1, port=5000)
        self.assertEqual("100.0", ret1.result().text)

        tasks = [f"offloading/{num}" for num in range(20, 50)]
        rets = []
        for task in tasks:
            rets.append(de.submit_task(task, port=5000))
        for i in range(20, 50):
            self.assertEqual(f"{float(i)**2}", rets[i-20].result().text)


if __name__ == '__main__':
    unittest.main()
