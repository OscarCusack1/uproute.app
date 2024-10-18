from .utils import convert_time_to_minutes

class Vehicle:
    def __init__(self, capacity:None, start_time:None, end_time:None):
        self.capacity = capacity
        self.start_time = convert_time_to_minutes(start_time)
        self.end_time = convert_time_to_minutes(end_time)