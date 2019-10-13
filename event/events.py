class Event:
    """
    本任务中的事件基类，均与顾客有关系
    """

    def __init__(self, object_, time, event_type: str):
        self.object = object_
        self.time = time
        self.event_type: str = event_type

    def __lt__(self, other):
        """
        内置的compare比较函数，用于实现优先队列
        """
        return self.time < other.get_time()

    def get_time(self):
        return self.time

    def get_object(self):
        return self.object

    def get_type(self):
        return self.event_type
