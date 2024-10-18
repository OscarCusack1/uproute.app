from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from functools import partial

class OptimiserJob:
    def __init__(self, distance_matrix, num_vehicles:int, demand_matrix:list[list]|None=None, capacity_matrix:list|None=None, schedule_matrix:list|None=None):
        self.distance_matrix = distance_matrix
        self.num_vehicles = num_vehicles
        self.start_index = [i for i in range(self.num_vehicles)]
        self.end_index = [i+len(self.distance_matrix) - self.num_vehicles for i in range(self.num_vehicles)]
        self.demand_matrix = demand_matrix if demand_matrix else [0] * len(self.distance_matrix)
        self.capacity_matrix = capacity_matrix
        self.schedule_matrix = schedule_matrix

        self.solve = partial(decide_solve_method(self.demand_matrix, self.capacity_matrix, self.schedule_matrix), self)
        print(self.solve)
        self.time_dimension = None
        self.capacity_dimension = None

        self.manager = pywrapcp.RoutingIndexManager(len(self.distance_matrix), self.num_vehicles, self.start_index, self.end_index) # Create the routing index manager
        self.routing = pywrapcp.RoutingModel(self.manager)

        self.solution = None


def decide_solve_method(demand_matrix, capacity_matrix, schedule_matrix):
    needs_demand = sum(demand_matrix) > 0 and sum(capacity_matrix) > 0
    for window in schedule_matrix:
        print(window)
    needs_schedule = all([all(window) for window in schedule_matrix])

    print(f'Demand: {needs_demand}, Schedule: {needs_schedule}')
    if not needs_demand and not needs_schedule:
        return solve_vrp
    if needs_demand and not needs_schedule:
        return solve_cvrp
    if needs_schedule and not needs_demand:
        return solve_vrptw
    if needs_demand and needs_schedule:
        return solve_cvrptw


def solve_vrp(job:OptimiserJob) -> None:

    # Create and register a transit callback
    def distance_callback(from_index, to_index):
        from_node = job.manager.IndexToNode(from_index)
        to_node = job.manager.IndexToNode(to_index)
        return job.distance_matrix[from_node][to_node]

    transit_callback_index = job.routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc
    job.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Set search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    # Set the lns
    search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(60)
    search_parameters.solution_limit = 100

    # Solve the problem
    job.solution = job.routing.SolveWithParameters(search_parameters)

def solve_cvrp(job:OptimiserJob):

    # Create and register a transit callback
    def distance_callback(from_index, to_index):
        from_node = job.manager.IndexToNode(from_index)
        to_node = job.manager.IndexToNode(to_index)
        return job.distance_matrix[from_node][to_node]

    transit_callback_index = job.routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc
    job.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add capacity constraint
    def demand_callback(from_index):
        from_node = job.manager.IndexToNode(from_index)
        return job.demand_matrix[from_node]

    demand_callback_index = job.routing.RegisterUnaryTransitCallback(demand_callback)
    job.routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        job.capacity_matrix,  # vehicle maximum capacity
        True,  # start cumul to zero
        'Capacity')
    
    job.capacity_dimension = job.routing.GetDimensionOrDie('Capacity')

    # Set search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    # Set the lns
    search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(60)
    search_parameters.solution_limit = 100

    # Solve the problem
    job.solution = job.routing.SolveWithParameters(search_parameters)
    
def solve_vrptw(job:OptimiserJob) -> None:

    # Create and register a transit callback
    def distance_callback(from_index, to_index):
        # Returns the distance between the two nodes
        from_node = job.manager.IndexToNode(from_index)
        to_node = job.manager.IndexToNode(to_index)
        return job.distance_matrix[from_node][to_node]

    transit_callback_index = job.routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc
    job.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Time Windows constraint
    def time_callback(from_index, to_index):
        # Returns the travel time between the two nodes
        from_node = job.manager.IndexToNode(from_index)
        to_node = job.manager.IndexToNode(to_index)
        return job.distance_matrix[from_node][to_node]

    time_callback_index = job.routing.RegisterTransitCallback(time_callback)

    job.routing.AddDimension(
        time_callback_index,
        180,  # allow waiting time
        86400,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        'Time')

    job.time_dimension = job.routing.GetDimensionOrDie('Time')

    # Add time window constraints for each location except depot
    for location_idx, time_window in enumerate(job.schedule_matrix):
        if location_idx in job.start_index or location_idx in job.end_index:
            continue
        index = job.manager.NodeToIndex(location_idx)
        job.time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # Add time window constraints for each vehicle start node
    for vehicle_id in range(job.num_vehicles):
        start_index = job.routing.Start(vehicle_id)
        end_index = job.routing.End(vehicle_id)
        job.time_dimension.CumulVar(start_index).SetRange(
            job.schedule_matrix[job.start_index[vehicle_id]][0],
            job.schedule_matrix[job.start_index[vehicle_id]][1]
        )
        job.time_dimension.CumulVar(end_index).SetRange(
            job.schedule_matrix[job.end_index[vehicle_id]][0],
            job.schedule_matrix[job.end_index[vehicle_id]][1]
        )
        job.routing.AddVariableMinimizedByFinalizer(
            job.time_dimension.CumulVar(job.routing.Start(vehicle_id)))
        job.routing.AddVariableMinimizedByFinalizer(
            job.time_dimension.CumulVar(job.routing.End(vehicle_id)))


    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(60)
    search_parameters.solution_limit = 100

    # Solve the problem
    job.solution = job.routing.SolveWithParameters(search_parameters)

def solve_cvrptw(job:OptimiserJob) -> None:

    # Create and register a transit callback
    def distance_callback(from_index, to_index):
        # Returns the distance between the two nodes
        from_node = job.manager.IndexToNode(from_index)
        to_node = job.manager.IndexToNode(to_index)
        return job.distance_matrix[from_node][to_node]

    transit_callback_index = job.routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc
    job.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add capacity constraint
    def demand_callback(from_index):
        from_node = job.manager.IndexToNode(from_index)
        return job.demand_matrix[from_node]

    demand_callback_index = job.routing.RegisterUnaryTransitCallback(demand_callback)
    job.routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        job.capacity_matrix,  # vehicle maximum capacity
        True,  # start cumul to zero
        'Capacity')
    
    job.capacity_dimension = job.routing.GetDimensionOrDie('Capacity')

    # Add Time Windows constraint
    def time_callback(from_index, to_index):
        # Returns the travel time between the two nodes
        from_node = job.manager.IndexToNode(from_index)
        to_node = job.manager.IndexToNode(to_index)
        return job.distance_matrix[from_node][to_node]

    time_callback_index = job.routing.RegisterTransitCallback(time_callback)

    job.routing.AddDimension(
        time_callback_index,
        180,  # allow waiting time
        86400,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        'Time')

    job.time_dimension = job.routing.GetDimensionOrDie('Time')

    # Add time window constraints for each location except depot
    for location_idx, time_window in enumerate(job.schedule_matrix):
        if location_idx in job.start_index or location_idx in job.end_index:
            continue
        index = job.manager.NodeToIndex(location_idx)
        job.time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # Add time window constraints for each vehicle start node
    for vehicle_id in range(job.num_vehicles):
        start_index = job.routing.Start(vehicle_id)
        end_index = job.routing.End(vehicle_id)
        job.time_dimension.CumulVar(start_index).SetRange(
            job.schedule_matrix[job.start_index[vehicle_id]][0],
            job.schedule_matrix[job.start_index[vehicle_id]][1]
        )
        job.time_dimension.CumulVar(end_index).SetRange(
            job.schedule_matrix[job.end_index[vehicle_id]][0],
            job.schedule_matrix[job.end_index[vehicle_id]][1]
        )
        job.routing.AddVariableMinimizedByFinalizer(
            job.time_dimension.CumulVar(job.routing.Start(vehicle_id)))
        job.routing.AddVariableMinimizedByFinalizer(
            job.time_dimension.CumulVar(job.routing.End(vehicle_id)))


    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(60)
    search_parameters.solution_limit = 100

    # Solve the problem
    job.solution = job.routing.SolveWithParameters(search_parameters)