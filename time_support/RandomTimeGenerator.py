import numpy as np


class RandomTimeGenerator:
    """
    随机时间生成器
    @拓展：
    1. 多类随机分布生成器
    """

    def __init__(self, mean, num):
        self.mean = mean
        self.num = num
        self.pointer = 0
        self.random_candidate = self.__random_sample__(mean, num)

    @staticmethod
    def __random_sample__(mean, num):
        """
        根据平均数和数量生成指定的随机数备选列表，这样做的目的是为了使得随机数尽可能接近均值
        :param mean: 均值
        :param num: 数量
        :return: 随机数备选列表
        """
        list = []
        for i in range(0, num):
            list.append(np.random.uniform(mean * 0.5, mean * 1.5))
        return list

    def next(self):
        # 若取出的次数超过预先约定的数量，会警告并生成新的一批备选值
        if self.pointer >= self.num:
            print("[WARNING]: times of next call exceed predefined number.")
            self.pointer = 0
            self.random_candidate = self.__random_sample__(self.mean, self.num)
        temp = self.random_candidate[self.pointer]
        self.pointer += 1
        return temp
