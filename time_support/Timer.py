class Timer:
    """
    全局时钟类
    """
    def __init__(self):
        self.time = 0

    def get_time(self):
        return self.time

    def forward(self, time):
        self.time = time

    def reset(self):
        self.time = 0
