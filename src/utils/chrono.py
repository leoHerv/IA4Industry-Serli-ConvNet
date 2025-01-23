import time

class Chrono:
    def __init__(self):
        self.start_v = None
        self.end_v = None

    def start(self):
        self.start_v = time.time()
        self.end_v = None

    def stop(self):
        if self.start_v is None:
            raise ValueError("Call start first.")
        self.end_v = time.time()
        time_val = self.end_v - self.start_v
        return time_val