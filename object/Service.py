from object.Customer import Customer
from time_support.Timer import Timer


class Service:
    """
    服务窗口类
    """

    def __init__(self, id, timer: Timer):
        self.id = id
        self.busy = False
        self.current_serving = None
        self.timer = timer  # 计时器
        self.record = []  # 服务记录表

    def isBusy(self):
        return self.busy

    def dump_and_load(self, customer):
        """
        结束当前乘客的服务，并载入新的服务对象（若为None则无）
        :param customer: 下一位待服务乘客（None）表示没有了。
        :return: 下一位乘客的预计服务结束时间，若无乘客则返回 None.
        """
        # 结束上一个顾客服务（如有）
        if self.current_serving:
            print("[DEBUG] {:.5f} customer service finished.".format(self.timer.get_time()))
            # 错误检查，服务时间是否对上了
            expected_time = self.current_serving.customer.service + self.current_serving.customer.begin_service_time
            if abs(self.timer.get_time() - expected_time) > 0.00001:
                print("[Error]: Current Time didn't match expected service time.")

        # 开始当前乘客服务 (如有)
        if not customer:
            self.current_serving = None
            self.busy = False
            return None
        else:
            # 开始服务
            customer.begin_service()
            # 新建一份服务表, 设置为当前服务对象，并加入服务记录中.
            new_record = ServiceRecord(customer=customer, enter_time=self.timer.get_time())
            self.record.append(new_record)
            self.current_serving = new_record
            self.busy = True

            return self.timer.get_time() + customer.service


class ServiceRecord:
    """
    服务记录单，详细地记录了服务的具体细节 (对象是谁？多久开始？多久结束？)
    """

    def __init__(self, customer: Customer, enter_time):
        self.customer = customer
        self.enter_time = enter_time
        self.leave_time = None

    def get_customer(self) -> Customer:
        return self.customer

    def finish_service(self, time):
        self.leave_time = time

    def get_service_time(self):
        return self.enter_time, self.leave_time
