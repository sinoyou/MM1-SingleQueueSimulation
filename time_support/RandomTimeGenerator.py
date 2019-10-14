import numpy as np
import random


class RandomTimeGenerator:
    """
    随机时间生成器
    @拓展：
    1. 多类随机分布生成器
    """

    def __init__(self, mean, num, dis_type):
        self.mean = mean
        self.num = num
        self.pointer = 0
        self.random_candidate = self.__random_sample__(mean, num, dis_type)
        self.dis_type = dis_type

    @staticmethod
    def __random_sample__(mean, num, dis_type):
        """
        根据平均数和数量生成指定的随机数备选列表，这样做的目的是为了使得随机数尽可能接近均值
        :param mean: 均值
        :param num: 数量
        :param dis_type: 分布选择
        :return: 随机数备选列表
        """
        if dis_type == "poisson":
            distribution = np.random.poisson(mean, num)
            random.shuffle(distribution)
            return distribution
        elif dis_type == "exp":
            distribution = np.random.exponential(mean, num)
            random.shuffle(distribution)
            return distribution
        else:
            print("[ERROR] Unknown random distribution.")

    def next(self):
        # 若取出的次数超过预先约定的数量，会警告并生成新的一批备选值
        if self.pointer >= self.num:
            print("[WARNING]: times of next call exceed predefined number.")
            self.pointer = 0
            self.random_candidate = self.__random_sample__(self.mean, self.num, self.dis_type)
        temp = self.random_candidate[self.pointer]
        self.pointer += 1
        return temp
