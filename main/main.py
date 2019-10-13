import queue
from event.events import Event
from object.Customer import Customer
from object.Service import Service
from time_support.Timer import Timer
from time_support.RandomTimeGenerator import RandomTimeGenerator

# --- 重要的全局变量 ---

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
wait_queue = []  # 顾客等待队列

# 全局时钟器
timer = Timer()


def initial_parameters():
    global mean_inter_arrival, mean_service, number_of_customs, max_queue_length, number_of_service
    mean_inter_arrival = 5.0
    mean_service = 10
    number_of_customs = 50
    max_queue_length = 10
    number_of_service = 1


def service_generate():
    for i in range(0, number_of_service):
        service_list.append(Service(id=i, timer=timer))


def customers_generate():
    # 定义<internal>随机数生成器和<service>随机数生成器
    inter_gen = RandomTimeGenerator(mean_inter_arrival, number_of_customs)
    service_gen = RandomTimeGenerator(mean_service, number_of_customs)
    cur_time = 0
    for i in range(0, number_of_customs):
        inter = inter_gen.next()
        service_time = service_gen.next()
        cur_time += inter
        c = Customer(id=i, timer=timer, arrive=cur_time, service=service_time)
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
                customer.enter_queue()
                if len(wait_queue) > max_queue_length:
                    print("[WARNING] Waiting queue is full")
                else:
                    wait_queue.append(customer)

        # 完成服务型 事件
        elif event.event_type == "FINISH":
            service = event.get_object()  # 获取事件的服务窗口
            customer = None if len(wait_queue) == 0 else wait_queue.pop(0)  # 获取排在服务队列里的下一个乘客
            next_finish_time = service.dump_and_load(customer)  # 更换服务对象并算出下一次“FINISH”事件发生的时刻
            if next_finish_time:
                finish_event = Event(object_=service, time=next_finish_time, event_type="FINISH")
                event_queue.put(finish_event)
                print("[DEBUG] {:.5f} event add FINISH {:.5f}".format(timer.get_time(), next_finish_time))

        else:
            print("[Error]: Unknown event type %s.".format(event.event_type))


def report():
    pass


if __name__ == "__main__":
    # Main part
    initial_parameters()
    service_generate()
    customers_generate()
    simulate()
