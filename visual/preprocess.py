import queue
import matplotlib.pyplot as plt
import numpy as np
from event.events import Event
from object.Customer import Customer
from object.Service import Service
from object.WaitQueue import WaitQueue
from time_support.Timer import Timer
from time_support.RandomTimeGenerator import RandomTimeGenerator

# --- 重要的全局变量 ---
# 全局时钟器
timer = Timer()

# 参数
mean_inter_arrival = 0  # 到达时间间隔的均值
mean_service = 0  # 服务时间的均值
number_of_customs = 0  # 顾客总人数
max_queue_length = 0  # 队列最大长度
number_of_service = 0  # 服务窗口数量

# 列表
custom_list = []  # 顾客列表，按照到达时间排列
service_list = []  # 服务器列表，默认为1

# 队列
event_queue = queue.PriorityQueue()  # 未来事件队列(FEL)，按照时间从小到大排序
wait_queue = WaitQueue(timer=timer)  # 顾客等待队列


def initial_parameters(mean_arrive=50.0, mean_serve=100.0, num_custom=100, max_queue=15, num_service=3):
    # initial value
    global mean_inter_arrival, mean_service, number_of_customs, max_queue_length, number_of_service
    mean_inter_arrival = mean_arrive
    mean_service = mean_serve
    number_of_customs = num_custom
    max_queue_length = max_queue
    number_of_service = num_service
    # clear
    global custom_list, service_list, timer, event_queue, wait_queue
    custom_list = []
    service_list = []
    wait_queue = WaitQueue(timer=timer)
    event_queue = queue.PriorityQueue()
    timer.reset()


def service_generate():
    for i in range(0, number_of_service):
        service_list.append(Service(id=i, timer=timer))


def customers_generate():
    # 定义<internal>随机数生成器和<service>随机数生成器
    inter_gen = RandomTimeGenerator(mean_inter_arrival, number_of_customs, "poisson")
    service_gen = RandomTimeGenerator(mean_service, number_of_customs, "exp")
    cur_time = 0
    for i in range(0, number_of_customs):
        inter = inter_gen.next()
        service_time = service_gen.next()
        cur_time += inter
        c = Customer(id=i, timer=timer, arrive=cur_time, arrive_inter=inter,
                     service=service_time)
        custom_list.append(c)
        print("Customer {} arrival {:.5f} service {:.5f}".format(i, cur_time, service_time))


def simulate():
    # step 1 : 向事件队列中加入所有<到达事件>
    for customer in custom_list:
        event = Event(object_=customer, time=customer.arrive, event_type="ARRIVE")
        event_queue.put(event)
        print("[DEBUG] {:.5f} event add ARRIVE {:.5f}".format(timer.get_time(), customer.arrive))

    # step 2 : 事件推进型仿真
    while not event_queue.empty():
        # 取出队头事件，并推进时间至事件发生时刻
        event = event_queue.get()
        timer.forward(event.get_time())
        # 乘客到达型 事件
        if event.event_type == "ARRIVE":
            customer = event.get_object()
            free_service = [service for service in service_list if not service.isBusy()]  # 查询是否有空闲窗口
            # 如果当前存在空闲窗口，则不排队直接去
            if len(free_service) > 0:
                # 选择一个空闲窗口， 前去服务并计算结束时间， 建立FINISH类型的事件队列
                target_service = free_service[0]
                next_finish_time = target_service.dump_and_load(customer)
                finish_event = Event(object_=target_service, time=next_finish_time, event_type="FINISH")
                event_queue.put(finish_event)
                print("[DEBUG] {:.5f} event add FINISH {:.5f}".format(timer.get_time(), next_finish_time))
            # 如果当前不存在空闲窗口，则排队(需要检查队列是否已满)
            else:
                if len(wait_queue) > max_queue_length:
                    print("[WARNING] Waiting queue is full")
                else:
                    customer.enter_queue()
                    wait_queue.append(customer)

        # 完成服务型 事件
        elif event.event_type == "FINISH":
            service = event.get_object()  # 获取事件的服务窗口
            customer = None if len(wait_queue) == 0 else wait_queue.pop()  # 获取排在服务队列里的下一个乘客
            next_finish_time = service.dump_and_load(customer)  # 更换服务对象并算出下一次“FINISH”事件发生的时刻
            if next_finish_time:
                finish_event = Event(object_=service, time=next_finish_time, event_type="FINISH")
                event_queue.put(finish_event)
                print("[DEBUG] {:.5f} event add FINISH {:.5f}".format(timer.get_time(), next_finish_time))

        else:
            print("[Error]: Unknown event type %s.".format(event.event_type))


def report_plot():
    plt.figure(figsize=(20, 30))
    plt.style.use('seaborn')
    # 乘客到达时间分布情况
    plt.subplot(3, 2, 1)
    plt.xlabel("arrival internal/s")
    plt.ylabel("number")
    plt.title("Customer Arrival Internal Time Distribution in {} Customers".format(len(custom_list)))
    arrive_time_list = [custom.arrive_inter for custom in custom_list]
    plt.hist(arrive_time_list)

    # 乘客服务时间分布情况
    plt.subplot(3, 2, 2)
    plt.xlabel("service time/s")
    plt.ylabel("number")
    plt.title("Customer Service Time Distribution in {} Customers".format(len(custom_list)))
    service_time_list = [custom.service for custom in custom_list]
    plt.hist(service_time_list)

    # 队列平均顾客数
    plt.subplot(3, 2, 3)
    plt.xlabel("time")
    plt.ylabel("average customers in queue")
    plt.title("Average Number Of Customers in Queue By time")
    ave_customer = []
    for i in range(0, int(timer.get_time())):
        ave_customer.append(wait_queue.get_ave_wait(time=i))
    plt.plot(range(0, int(timer.get_time())), ave_customer)

    # 服务器平均利用率
    plt.subplot(3, 2, 4)
    plt.xlabel("time")
    plt.ylabel("average usage in queue")
    plt.title("Average Service Time By time")
    for service in service_list:
        ave_service = []
        for i in range(0, int(timer.get_time())):
            ave_service.append(service.get_ave_usage(i))
        plt.plot(range(0, int(timer.get_time())), ave_service)

    # 顾客去留情况
    plt.subplot(3, 1, 3)
    plt.title("Served Customers's Distribution By time")
    for (i, custom) in enumerate(custom_list):
        if custom.begin_service_time:
            time_start = int(custom.arrive)
            time_end = int(custom.begin_service_time + custom.service)
            x = range(time_start, time_end + 1)
            y = np.full((time_end - time_start + 1), i + 1)
            plt.scatter(x, y)
        else:
            plt.scatter(custom.arrive, i + 1)

    plt.show()


def report_print():
    # 乘客平均服务时间
    total_custom = len(custom_list)
    service_custom_list = [custom for custom in custom_list if custom.begin_service_time]
    service_num = len(service_custom_list)
    no_service_num = total_custom - len(service_custom_list)
    print("[REPORT] {}({:.3f}) customers leave due to overflow of queue.".
          format(no_service_num, no_service_num / total_custom))
    count = 0
    for custom in service_custom_list:
        count += custom.get_wait_length() + custom.service
    print("[REPORT] average service process for served customers is {:3f}".format(count / service_num))

    return count / service_num, no_service_num / total_custom


def task_simulate():
    initial_parameters()
    service_generate()
    customers_generate()
    simulate()
    report_print()
    report_plot()


def task_parameter():
    # 尝试不同的服务时间对均值的影响
    service_mean_list = np.arange(5.0, 10.0, 0.1)
    mean_length_list = []
    no_service_list = []
    for service_mean in service_mean_list:
        initial_parameters(mean_serve=service_mean)
        service_generate()
        customers_generate()
        simulate()
        mean_length, no_service = report_print()
        mean_length_list.append(mean_length)
        no_service_list.append(no_service)

    plt.style.use('seaborn')

    plt.subplot(1, 2, 1)
    plt.title("Mean Service Length Trend")
    plt.plot(service_mean_list, mean_length_list)

    plt.subplot(1, 2, 2)
    plt.title("No Service Trend")
    plt.plot(service_mean_list, no_service_list)

    plt.show()


if __name__ == "__main__":
    # Main part
    task_simulate()
    # task_parameter()
