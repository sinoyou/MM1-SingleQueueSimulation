import queue
import matplotlib.pyplot as plt
import numpy as np
from main.utils import debug_print
from event.events import Event
from object.Customer import Customer
from object.Service import Service
from object.WaitQueue import WaitQueue
from time_support.Timer import Timer
from time_support.RandomTimeGenerator import RandomTimeGenerator


class Global:
    def __init__(self):
        # --- 重要的全局变量 ---
        # 全局时钟器
        self.timer = Timer()

        # 参数
        self.mean_inter_arrival = 0  # 到达时间间隔的均值
        self.mean_service = 0  # 服务时间的均值
        self.number_of_customs = 0  # 顾客总人数
        self.max_queue_length = 0  # 队列最大长度
        self.number_of_service = 0  # 服务窗口数量

        # 列表
        self.custom_list = []  # 顾客列表，按照到达时间排列
        self.service_list = []  # 服务器列表，默认为1

        # 队列
        self.event_queue = queue.PriorityQueue()  # 未来事件队列(FEL)，按照时间从小到大排序
        self.wait_queue = WaitQueue(timer=self.timer)  # 顾客等待队列

    def initial_parameters(self, mean_arrive=50.0, mean_serve=100.0, num_custom=100, max_queue=15, num_service=1):
        # initial value
        self.mean_inter_arrival = mean_arrive
        self.mean_service = mean_serve
        self.number_of_customs = num_custom
        self.max_queue_length = max_queue
        self.number_of_service = num_service
        # clear
        self.custom_list.clear()
        self.service_list.clear()
        self.wait_queue = WaitQueue(timer=self.timer)
        self.event_queue = queue.PriorityQueue()
        self.timer.reset()

    def service_generate(self):
        for i in range(0, self.number_of_service):
            self.service_list.append(Service(id=i, timer=self.timer))

    def customers_generate(self):
        # 定义<internal>随机数生成器和<service>随机数生成器
        inter_gen = RandomTimeGenerator(self.mean_inter_arrival, self.number_of_customs, "exp", shuffle=False)
        service_gen = RandomTimeGenerator(self.mean_service, self.number_of_customs, "exp")
        cur_time = 0
        for i in range(0, self.number_of_customs):
            inter = inter_gen.next()
            service_time = service_gen.next()
            c = Customer(id=i, timer=self.timer, arrive=cur_time, arrive_inter=inter,
                         service=service_time)
            self.custom_list.append(c)
            cur_time += inter
            debug_print("Customer {} arrival {:.5f} service {:.5f}".format(i, cur_time, service_time))

    def simulate(self):
        # step 1 : 向事件队列中加入所有<到达事件>
        for customer in self.custom_list:
            event = Event(object_=customer, time=customer.arrive, event_type="ARRIVE")
            self.event_queue.put(event)
            debug_print("[DEBUG] {:.5f} event add ARRIVE {:.5f}".format(self.timer.get_time(), customer.arrive))

        # step 2 : 事件推进型仿真
        while not self.event_queue.empty():
            # 取出队头事件，并推进时间至事件发生时刻
            event = self.event_queue.get()
            self.timer.forward(event.get_time())
            # 乘客到达型 事件
            if event.event_type == "ARRIVE":
                customer = event.get_object()
                free_service = [service for service in self.service_list if not service.isBusy()]  # 查询是否有空闲窗口
                # 如果当前存在空闲窗口，则不排队直接去
                if len(free_service) > 0:
                    # 选择一个空闲窗口， 前去服务并计算结束时间， 建立FINISH类型的事件队列
                    np.random.shuffle(free_service)
                    target_service = free_service[0]
                    next_finish_time = target_service.dump_and_load(customer)
                    finish_event = Event(object_=target_service, time=next_finish_time, event_type="FINISH")
                    self.event_queue.put(finish_event)
                    debug_print(
                        "[DEBUG] {:.5f} event add FINISH {:.5f}".format(self.timer.get_time(), next_finish_time))
                # 如果当前不存在空闲窗口，则排队(需要检查队列是否已满)
                else:
                    if len(self.wait_queue) > self.max_queue_length:
                        debug_print("[WARNING] Waiting queue is full")
                    else:
                        customer.enter_queue()
                        self.wait_queue.append(customer)

            # 完成服务型 事件
            elif event.event_type == "FINISH":
                service = event.get_object()  # 获取事件的服务窗口
                customer = None if len(self.wait_queue) == 0 else self.wait_queue.pop()  # 获取排在服务队列里的下一个乘客
                next_finish_time = service.dump_and_load(customer)  # 更换服务对象并算出下一次“FINISH”事件发生的时刻
                if next_finish_time:
                    finish_event = Event(object_=service, time=next_finish_time, event_type="FINISH")
                    self.event_queue.put(finish_event)
                    debug_print(
                        "[DEBUG] {:.5f} event add FINISH {:.5f}".format(self.timer.get_time(), next_finish_time))

            else:
                debug_print("[Error]: Unknown event type %s.".format(event.event_type))

    # 定义report的图表结果部分
    def report_plot(self):
        plt.figure(figsize=(12, 15))
        plt.style.use('seaborn')
        # 乘客到达时间分布情况
        plt.subplot(3, 2, 1)
        plt.xlabel("arrival internal/s")
        plt.ylabel("number")
        plt.title("Customer Arrival Internal Time Distribution in {} Customers".format(len(self.custom_list)))
        arrive_time_list = [custom.arrive_inter for custom in self.custom_list]
        plt.hist(arrive_time_list)

        # 乘客服务时间分布情况
        plt.subplot(3, 2, 2)
        plt.xlabel("service time/s")
        plt.ylabel("number")
        plt.title("Customer Service Time Distribution in {} Customers".format(len(self.custom_list)))
        service_time_list = [custom.service for custom in self.custom_list]
        plt.hist(service_time_list)

        # 队列平均顾客数
        plt.subplot(3, 2, 3)
        plt.xlabel("time")
        plt.ylabel("average customers in queue")
        plt.title("Average Number Of Customers in Queue By time")
        ave_customer = []
        for i in range(1, int(self.timer.get_time())):
            ave_customer.append(self.wait_queue.get_ave_wait(time=i))
        plt.plot(range(1, int(self.timer.get_time())), ave_customer)

        # 服务器平均利用率
        plt.subplot(3, 2, 4)
        plt.xlabel("time")
        plt.ylabel("average usage in queue")
        plt.title("Average Service Time By time")
        for service in self.service_list:
            ave_service = []
            for i in range(1, int(self.timer.get_time())):
                ave_service.append(service.get_ave_usage(i))
            plt.plot(range(1, int(self.timer.get_time())), ave_service)

        # 顾客去留情况
        if len(self.custom_list) <= 200:
            plt.subplot(3, 1, 3)
            plt.title("Served Customers's Distribution By time")
            for (i, custom) in enumerate(self.custom_list):
                if custom.begin_service_time:
                    time_start = int(custom.arrive)
                    time_end = int(custom.begin_service_time + custom.service)
                    x = range(time_start, time_end + 1)
                    y = np.full((time_end - time_start + 1), i + 1)
                    plt.scatter(x, y)
                else:
                    plt.scatter(custom.arrive, i + 1)

        plt.show()

    # 定义report的数值结果部分
    def report_print(self, is_print=False):
        # 乘客平均服务时间
        total_custom = len(self.custom_list)
        service_custom_list = [custom for custom in self.custom_list if custom.begin_service_time]
        service_num = len(service_custom_list)
        no_service_num = total_custom - len(service_custom_list)
        count = 0
        for custom in service_custom_list:
            count += custom.get_wait_length() + custom.service

        if is_print:
            print("[REPORT] {}({:.3f}) customers leave due to overflow of queue.".
                  format(no_service_num, no_service_num / total_custom))
            print("[REPORT] average service process for served customers is {:3f}".format(count / service_num))

        return count / service_num, no_service_num / total_custom

    # 任务: 仿真
    def task_simulate(self, x, y, z, m, n):
        self.initial_parameters(x, y, z, m, n)
        self.service_generate()
        self.customers_generate()
        self.simulate()
        self.report_print(True)  # 打印量化结果：顾客的平均逗留时间，队列溢出乘客比例
        self.report_plot()  # 显示可视化结果

    # 任务: 调整输入参数的入口 - 平均服务时长
    def task_parameter_of_service_mean(self, x, service_mean_list, z, m, service_num_list):
        plt.style.use('seaborn')
        plt.figure(figsize=(10, 6))

        # 尝试不同的服务时间对均值的影响
        list_by_service = []
        for service_num in service_num_list:
            mean_length_list = []
            no_service_list = []
            for service_mean in service_mean_list:
                self.initial_parameters(x, service_mean, z, m, service_num)
                self.service_generate()
                self.customers_generate()
                self.simulate()
                mean_length, no_service = self.report_print()
                mean_length_list.append(mean_length)
                no_service_list.append(no_service)
            list_by_service.append((service_num, mean_length_list, no_service_list))

        plt.subplot(1, 2, 1)
        plt.title("Mean Service Length Trend")
        for (service_num, mean_length_list, no_service_list) in list_by_service:
            plt.plot(service_mean_list, mean_length_list, label=str(service_num))

        plt.subplot(1, 2, 2)
        plt.title("No Service Trend")
        for (service_num, mean_length_list, no_service_list) in list_by_service:
            plt.plot(service_mean_list, no_service_list, label=str(service_num))

        plt.legend()
        plt.show()

    # 任务: 调整输入参数的入口 - 平均到达时间间隔
    def task_parameter_of_arrival_mean(self, internal_mean_list, y, z, m, n):
        # 尝试不同的服务时间对均值的影响
        mean_length_list = []
        no_service_list = []
        for internal_mean in internal_mean_list:
            self.initial_parameters(internal_mean, y, z, m, n)
            self.service_generate()
            self.customers_generate()
            self.simulate()
            mean_length, no_service = self.report_print()
            mean_length_list.append(mean_length)
            no_service_list.append(no_service)

        plt.style.use('seaborn')
        plt.figure(figsize=(10, 6))

        plt.subplot(1, 2, 1)
        plt.title("Mean Service Length Trend")
        plt.plot(internal_mean_list, mean_length_list)

        plt.subplot(1, 2, 2)
        plt.title("No Service Trend")
        plt.plot(internal_mean_list, no_service_list)

        plt.show()

    # 任务: 调整输入参数的入口 - 服务窗口数量
    def task_parameter_of_queue_size(self, x, y, z, queue_size_list, service_num_list):
        plt.style.use('seaborn')
        plt.figure(figsize=(10, 6))

        # 尝试不同的服务时间对均值的影响
        list_by_service = []
        for service_num in service_num_list:
            mean_length_list = []
            no_service_list = []
            for queue_size in queue_size_list:
                self.initial_parameters(x, y, z, queue_size, service_num)
                self.service_generate()
                self.customers_generate()
                self.simulate()
                mean_length, no_service = self.report_print()
                mean_length_list.append(mean_length)
                no_service_list.append(no_service)
            list_by_service.append((service_num, mean_length_list, no_service_list))

        plt.subplot(1, 2, 1)
        plt.title("Mean Service Length Trend")
        for (service_num, mean_length_list, no_service_list) in list_by_service:
            plt.plot(queue_size_list, mean_length_list, label=str(service_num))

        plt.subplot(1, 2, 2)
        plt.title("No Service Trend")
        for (service_num, mean_length_list, no_service_list) in list_by_service:
            plt.plot(queue_size_list, no_service_list, label=str(service_num))

        plt.legend()
        plt.show()
