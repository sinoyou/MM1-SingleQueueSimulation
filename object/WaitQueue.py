import queue

from object.Customer import Customer


class WaitQueue:
    def __init__(self, timer):
        self.timer = timer
        self.queue = []
        self.record = []
        self.record_ptr = 0

    def __len__(self):
        return len(self.queue)

    def append(self, x: Customer):
        self.queue.append(x)
        self.record.append(WaitRecord(x, self.timer.get_time()))

    def pop(self):
        self.record[self.record_ptr].leave_queue(time=self.timer.get_time())
        self.record_ptr += 1
        return self.queue.pop(0)

    def get_ave_wait(self, time):
        """
        返回指定时刻的队列平均顾客数量
        :param time: 指定时刻
        :return: [0,time]的队列平均顾客数量
        """
        square = 0
        for record in self.record:
            if record.leave_time < time:
                square += record.leave_time - record.enter_time
            elif record.enter_time < time < record.leave_time:
                square += time - record.enter_time
        return square / time if time > 0 else 0


class WaitRecord:
    def __init__(self, customer, enter_time):
        self.enter_time = enter_time
        self.leave_time = None
        self.customer = customer

    def leave_queue(self, time):
        self.leave_time = time
