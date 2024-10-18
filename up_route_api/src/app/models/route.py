from .node import Node
from .optimiser import OptimiserJob
from pprint import pprint

class Route:
    def __init__(self, *nodes:Node):
        self.nodes = nodes

    def format_routes(self, job:OptimiserJob):
        if not job.solution:
            print("No Solution Found")
            return None
    
        self.use_demand = True if job.capacity_dimension else False
        self.use_time_windows = True if job.time_dimension else False
        
        print("Solution Found -> Objective: ", job.solution.ObjectiveValue())
        vehicles = []
        for vehicle_id in range(job.num_vehicles):
            start_index = job.routing.Start(vehicle_id) # first index (start loc)
            node = job.manager.IndexToNode(start_index) # first node (start loc)
            if job.time_dimension:
                # time_var = job.time_dimension.CumulVar(start_index)
                start_leave_time = job.solution.Max(job.time_dimension.CumulVar(start_index))
                print(f"Vehicle {vehicle_id} starts at {start_leave_time} minutes")
                shift_start = job.schedule_matrix[job.start_index[vehicle_id]][0]
                wait_time = start_leave_time - shift_start
            else:
                start_leave_time = 0
                shift_start = 0
                wait_time = 0
            index = job.solution.Value(job.routing.NextVar(start_index)) # second index (first stop)
            first_stop_node = job.manager.IndexToNode(index) # second node (first stop)
            start_dict = {
                'address': self.nodes[node].address,
                'latitude': self.nodes[node].latitude,
                'longitude': self.nodes[node].longitude,
                'arrival_time': start_leave_time,
                'depart_time': start_leave_time,
                'wait_time': wait_time,
                'time_to_next_stop': job.distance_matrix[node][first_stop_node],
                'time_from_previous_stop': 0,
                'demand': job.demand_matrix[node],
            }
            print(f"Vehicle {vehicle_id} starts at {start_dict['depart_time']} minutes")
            
            stops = []
            cumul_demand = 0
            arrive_time = 0
            leave_time = 0
            while not job.routing.IsEnd(index):
                next_node = job.manager.IndexToNode(index)
                previous_duration = job.distance_matrix[node][next_node]
                node = next_node
                location = self.nodes[node].address
                # print(f"Vehicle {vehicle_id} at {location}")
                next_index = job.solution.Value(job.routing.NextVar(index))

                demand = job.demand_matrix[node]
                cumul_demand += demand
                duration = job.distance_matrix[node][job.manager.IndexToNode(next_index)]
                if job.time_dimension:
                    time_var = job.time_dimension.CumulVar(start_index)
                    arrive_time = job.solution.Min(time_var)
                    leave_time = job.solution.Max(time_var)
                    wait_time = leave_time - arrive_time
                else:
                    arrive_time += previous_duration
                    leave_time += previous_duration
                    wait_time = 0
                cumul_duration = leave_time - start_leave_time
                # print(f"Distance to next location: {duration} minutes")
                stops.append({
                    'address': location,
                    'latitude': self.nodes[node].latitude,
                    'longitude': self.nodes[node].longitude,
                    'time_from_previous_stop': previous_duration,
                    'time_to_next_stop': duration,
                    'wait_time': wait_time,
                    'demand': demand,
                    'cumulative_demand': cumul_demand,
                    'cumulative_duration': cumul_duration,
                    'arrival_time': arrive_time,
                    'depart_time': leave_time
                })
                index = next_index
            if len(stops) == 0:
                duration = job.distance_matrix[node][job.manager.IndexToNode(index)]
            node = job.manager.IndexToNode(index)
            if job.time_dimension:
                time_var = job.time_dimension.CumulVar(index)
                arrive_time = job.solution.Min(time_var)
                vehicle_duration = arrive_time - start_leave_time
            else:
                arrive_time += duration
                vehicle_duration = arrive_time
            end_dict = {
                'address': self.nodes[node].address,
                'latitude': self.nodes[node].latitude,
                'longitude': self.nodes[node].longitude,
                'arrival_time': arrive_time,
                'depart_time': arrive_time,
                'wait_time': 0,
                'time_from_previous_stop': duration,
                'time_to_next_stop': 0,
                'demand': job.demand_matrix[node],
            }
            if job.time_dimension:
                shift_end = job.schedule_matrix[job.start_index[vehicle_id]][1]
            else:
                shift_end = vehicle_duration
            route = {
                'start_location': start_dict,
                'end_location': end_dict,
                'locations': stops,
                'vehicle_demand': cumul_demand,
                'vehicle_duration': vehicle_duration,
                'start_time': shift_start,
                'end_time': shift_end,
                'depart_time': start_leave_time,
                'arrival_time': arrive_time,
                'number_of_stops': len(stops),
                'capacity': job.capacity_matrix[vehicle_id]
            }
            vehicles.append(route)

        routes = {
            'vehicles': vehicles,
            'total_duration': sum(route['vehicle_duration'] for route in vehicles),
            'max_duration': max(route['vehicle_duration'] for route in vehicles),
            'latest_arrival': max(route['arrival_time'] for route in vehicles),
            'total_demand': sum(route['vehicle_demand'] for route in vehicles),
            'max_demand': max(route['vehicle_demand'] for route in vehicles),
            'total_stops': sum(route['number_of_stops'] for route in vehicles),
            'max_stops': max(route['number_of_stops'] for route in vehicles),
            'use_demand': self.use_demand,
            'use_time_windows': self.use_time_windows
        }
        pprint(routes)
        
        return routes