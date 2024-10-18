from .utils import convert_time_to_minutes

class Node:
    def __init__(self, address: str, demand: int=0, window_start=None, window_end=None, latitude:float|None=None, longitude:float|None=None):
        self.address = address
        self.demand = demand
        self.window_start = convert_time_to_minutes(window_start)
        self.window_end = convert_time_to_minutes(window_end)
        self.latitude = latitude
        self.longitude = longitude