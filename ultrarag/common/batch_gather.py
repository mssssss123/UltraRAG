import queue
from typing import Callable
from threading import Thread, Condition
import asyncio

class SingleTask:
    def __init__(self, info: list) -> None:
        """Initialize a single task with input information
        
        Args:
            info (list): Input data for the task
        """
        self.cond = Condition()
        self.info = info  # Input data
        self.exp = None   # Exception if any occurs
        self.res = None   # Output result

    def put_res(self, res):
        self.res = res
        with self.cond:
            self.cond.notify()

    def put_exp(self, exp):
        self.exp = exp
        with self.cond:
            self.cond.notify()

    def get_res(self):
        with self.cond:
            self.cond.wait()
            if self.exp:
                raise self.exp
            else:
                return self.res

class BatchGather:
    def __init__(
            self, 
            batch_func: Callable[[list], list], 
            batch_size=128, 
            max_capacity=256, 
            is_coroutine=False
    ) -> None:
        """Initialize BatchGather for processing tasks in batches
        
        Args:
            batch_func (Callable): Function to process batched inputs
            batch_size (int): Maximum size of each batch
            max_capacity (int): Maximum queue capacity
            is_coroutine (bool): Whether batch_func is a coroutine
        """
        self.task_queue = queue.Queue(max_capacity)
        self.batch_func = batch_func
        self.batch_size = batch_size
        self.loop_finish = True
        self.thread = None
        self.is_coroutine = is_coroutine

    def put_task(self, info):
        task = SingleTask(info)
        self.task_queue.put(task)
        return task

    def start(self):
        self.loop_finish = False
        self.thread = Thread(target=self._loop)
        self.thread.start()

    def stop(self):
        if self.loop_finish == False:
            print('stop batch gather')
            self.loop_finish = True
            self.task_queue.put(SingleTask([]))
            self.thread.join()
            self.thread = None

    def _get_task_batch(self):
        """Collect tasks into a batch up to batch_size
        
        Returns:
            tuple: (list of inputs, list of SingleTask objects)
        """
        self.last_task: SingleTask | None
        inputs = []
        tasks: list[SingleTask] = []
        
        # Get first task (blocking if queue is empty)
        if self.last_task is None:
            try:
                self.last_task = self.task_queue.get(False)
            except queue.Empty:
                self.last_task = self.task_queue.get(True)
                
        # Collect tasks until batch is full
        while True:
            tasks.append(self.last_task)
            inputs.extend(self.last_task.info)
            try:
                self.last_task = self.task_queue.get(False)
            except queue.Empty:
                self.last_task = None
                break
            if len(inputs) + len(self.last_task.info) > self.batch_size:
                break
        return inputs, tasks

    def _loop(self):
        self.last_task = None
        while True:
            inputs, tasks = self._get_task_batch()

            if self.loop_finish:
                return

            try:
                if self.is_coroutine:
                    result_batch = asyncio.run(self.batch_func(inputs))
                else:
                    result_batch = self.batch_func(inputs)
                assert isinstance(result_batch, list),  \
                    'batch gather result must be a list, now its [{}]'.format(type(result_batch))
                assert len(result_batch) == len(inputs), \
                    'batch gather result length must equal to input [{}], now its [{}]'.format(type(len(inputs), len(result_batch)))
                for item in tasks:
                    item_res, result_batch = result_batch[:len(item.info)], result_batch[len(item.info):]
                    item.put_res(item_res)
            except Exception as e:
                for item in tasks:
                    item.put_exp(e)

            if self.loop_finish:
                return
