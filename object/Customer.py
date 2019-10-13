class Customer:
    def __init__(self, id, timer, arrive, service):
        """
        顾客类
        :param timer: 全局计时器
        :param arrive: 顾客到达的绝对时间
        :param service: 顾客服务时间
        """
        self.id = id
        self.timer = timer
        self.arrive = arrive
        self.service = service

        self.begin_wait_time = None  # optional
        self.begin_service_time = None  # must

    def enter_queue(self):
        self.begin_service_time = self.timer.get_time()

    def begin_service(self):
        self.begin_service_time = self.timer.get_time()
