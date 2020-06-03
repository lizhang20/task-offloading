import unittest
from queue import Queue
from threading import Thread

from server import ServerList, Server
from engine import TaskInfo, DecisionEngine
from taskqueue import TaskQueue


class TaskQueueTestCase(unittest.TestCase):
    # def test_offloading_task_using_pure_Queue(self):
    #     q = Queue()
    #     server_list = ServerList()
    #     taskqueue = TaskQueue(q)
    #
    #     # before you run this test case
    #     # run a simple flask server with
    #     # "http://127.0.0.1:5000/" return "Hello, world!"
    #     taskinfo1 = TaskInfo(Server("PC", "127.0.0.1"), "", 5000)
    #     q.put(taskinfo1)
    #
    #     ret = taskqueue.offload_task()
    #     self.assertEqual("Hello, world!", ret.text)
    #
    # def test_offloading_task_using_decision_engine(self):
    #     q = Queue()
    #     server_list = ServerList()
    #     taskqueue = TaskQueue(q)
    #
    #     de = DecisionEngine(decision_algorithm="default", task_queue=q,
    #                         server_list=server_list)
    #     # when task="" represents that only access
    #     de.add_task_to_queue(task="", ip="127.0.0.1", port=5000)
    #
    #     self.assertFalse(q.empty())
    #
    #     ret = taskqueue.offload_task()
    #     self.assertEqual("Hello, world!", ret.text)

    def test_offload_task(self):
        q = Queue()
        tq = TaskQueue(q)

        task_info_1 = TaskInfo(Server("PC", "127.0.0.1"), "", 5000)

        ret = tq.offload_task(task_info_1)
        self.assertEqual("Hello, world!", ret.text)

    # def test_run(self):
    #     q = Queue()
    #     tq = TaskQueue(q)
    #
    #     tasks = [TaskInfo(Server(f"Pc{i}", "127.0.0.1"), f"/offloading/{i}", 5000) for i in range(100)]
    #     print(tasks)
    #     self.assertEqual(100, len(tasks))
    #
    #     thread = Thread(target=tq.run)
    #     thread.start()
    #
    #     for task in tasks:
    #         q.put(task)
    #
    #     q.join()

    def test_invoke_task_offloading_using_engine(self):
        pass


if __name__ == '__main__':
    unittest.main()
