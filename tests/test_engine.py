import unittest
from queue import Queue

from engine import DecisionEngine
from server import ServerList, Server
from config import Config


class EngineTestCase(unittest.TestCase):
    def test_engine_initialization(self):
        q = Queue()
        server_list = ServerList()
        # decision algorithm 0
        da = Config.decision_algorithm

        for key, value in da.items():
            de = DecisionEngine(decision_algorithm=key, task_queue=q, server_list=server_list)
            self.assertEqual(de.decision_func, value)

    def test_choose_server(self):
        q = Queue()
        server_list = ServerList.specify_server_list({
            "PC": "127.0.0.1",
        })
        de = DecisionEngine(decision_algorithm="default", task_queue=q, server_list=server_list)

        chosen_server = de.choose_server()
        self.assertEqual("PC", chosen_server.serverName)
        self.assertEqual("127.0.0.1", chosen_server.serverIP)

    def test_submit_task(self):
        q = Queue()
        server_list = ServerList()
        de = DecisionEngine(decision_algorithm="minimum_ping_delay", task_queue=q, server_list=server_list)

        task1 = "offloading/10"
        ret1 = de.submit_task(task1, port=5000)
        self.assertEqual("100.0", ret1.result().text)

        tasks = [f"offloading/{num}" for num in range(20, 50)]
        rets = []
        for task in tasks:
            rets.append(de.submit_task(task, port=5000))
        for i in range(20, 50):
            self.assertEqual(f"{float(i) ** 2}", rets[i - 20].result().text)


if __name__ == '__main__':
    unittest.main()
