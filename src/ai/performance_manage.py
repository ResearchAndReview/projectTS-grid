import math

class PerformanceManager:
    def __init__(self, init_perf, alpha=0.25):
        self.perf = init_perf
        self.alpha = alpha

    def update(self, calc_perf):
        delta = calc_perf - self.perf
        self.perf += delta * math.tanh(calc_perf * self.alpha)