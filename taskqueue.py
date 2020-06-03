# This is task queue module for accepting all tasks to send to specific server.
# A thread will block and detects that whether this queue is empty.
# If not, send this tasks and get feedback from server.

from queue import Queue
from concurrent.futures import ThreadPoolExecutor

from loguru import logger
import requests

from engine import TaskInfo


class TaskQueue:
    def __init__(self, task_queue: Queue):
        self.task_queue = task_queue
        # self.pool = ThreadPoolExecutor(10)

    def offload_task(self, data: TaskInfo):
        """
        Send task to remote server.
        Most times we use requests.get() method call some interface.

        :return: Result that remote server send back to us. Note that this is
                 response of requests.get() method. So when you print this response,
                 you will get a HTTP response code.
        """
        # data is a TaskInfo(server: Server, task: str, port: int)
        # data = self.task_queue.get()
        logger.info(f"Get task {data} and start offloading")

        server = data.server
        task = data.task
        port = data.port

        logger.info(f"Call remote server {server.serverIP}:{port} with task {task}")
        r = requests.get(f"http://{server.serverIP}:{port}/{task}")

        # r.__repr__() is "<Response [200]>"
        # r.text is the real text
        return r

    # def run(self):
    #     """
    #     Check whether task_queue has an item, get item out and submit it to thread
    #     pool.
    #     :return: None
    #     """
    #     while True:
    #         data = self.task_queue.get()
    #         logger.info(f"Get task {data} from task_queue, submit it to thread_pool")
    #         self.pool.submit(self.offload_task, data)
    #         # Indicates that this task has finished
    #         self.task_queue.task_done()
