from flask import jsonify, Blueprint, request
import asyncio

from .models.geo import get_coordinates, create_distance_matrix, calculate_distances
from .models.node import Node
from .models.vehicle import Vehicle
from .models.optimiser import OptimiserJob
from .models.route import Route
from .models.visuals import create_map

from .auth.api_auth import require_api_key, create_api_key

bp = Blueprint('main', __name__)

@bp.route('/api/test', methods=['GET'])
async def home():
    return jsonify({'message': 'ping'})

@bp.route('/api/create_routes_api_key', methods=['POST'])
async def new_api_key():
    data = request.get_json()
    print(data)
    if 'email' not in data:
        return jsonify({'error': 'No email provided'}), 400
    
    msg, code = create_api_key(data['email'])
    print(msg, code)
    return jsonify(**msg), code

@bp.route('/api/optimise_route', methods=['POST'])
@require_api_key
async def optimise_route():

    data = request.get_json()
    print(data)
    if 'locations' not in data or not data['locations']:
        return jsonify({'error': 'No locations provided'}), 400
    if 'vehicles' not in data or not data['vehicles']:
        return jsonify({'error': 'No vehicles provided'}), 400
    if 'start_location' not in data:
        return jsonify({'error': 'No start location provided'}), 400
    
    locations = data.get('locations')
    vehicles = data.get('vehicles')
    start_location = data.get('start_location')
    end_location = data.get('end_location', start_location)
    
    nodes:list[Node] = []
    for vehicle in vehicles:
        nodes.append(Node(start_location.get('address'), 0, vehicle.get('start_time'), vehicle.get('end_time'), start_location.get('latitude'), start_location.get('longitude')))
    # nodes = [Node(start_location.get('address'), 0, start_location.get('window_start'), start_location.get('window_end'))]
    nodes.extend([Node(location.get('address'), location.get('demand', 0), location.get('window_start'), location.get('window_end'), location.get('latitude'), location.get('longitude')) for location in locations])
    for vehicle in vehicles:
        nodes.append(Node(end_location.get('address'), 0, vehicle.get('start_time'), vehicle.get('end_time'), end_location.get('latitude'), end_location.get('longitude')))
    # nodes.append(Node(end_location.get('address'), 0, end_location.get('window_start'), end_location.get('window_end')))
    
    vehicles = [Vehicle(vehicle.get('capacity'), vehicle.get('start_time'), vehicle.get('end_time')) for vehicle in vehicles]

    if all((location.latitude and location.longitude) for location in nodes):
        coords = [(location.latitude, location.longitude) for location in nodes]
    else:
        coords = await asyncio.gather(*[get_coordinates(node) for node in nodes])
        for node in nodes:
            node.latitude, node.longitude = coords[nodes.index(node)]
    distance_matrix = create_distance_matrix(coords)

    demand_matrix = [node.demand for node in nodes]
    capacity_matrix = [vehicle.capacity for vehicle in vehicles]
    schedule_matrix = [(node.window_start, node.window_end) for node in nodes]
    optimiser_job = OptimiserJob(distance_matrix, len(vehicles), demand_matrix=demand_matrix, capacity_matrix=capacity_matrix, schedule_matrix=schedule_matrix)
    optimiser_job.solve()
    if not optimiser_job.solution:
        return jsonify({'error': 'No solution found'}), 400
    start_route = Route(*nodes, )
    routes = start_route.format_routes(optimiser_job)
    return jsonify(routes)

@bp.route('/api/route', methods=['GET'])
@require_api_key
async def get_optimise_route():
    # Call the optimise_route function to get the routes
    data = request.get_json()

    vehicles = data.get('vehicles', [])
    routes_coords = []
    for vehicle in vehicles:
        route_coords = []
        route_coords.append([vehicle.get('start_location').get('latitude'), vehicle.get('start_location').get('longitude')])
        locations = vehicle.get('locations')
        for location in locations:
            route_coords.append([location.get('latitude'), location.get('longitude')])
        route_coords.append([vehicle.get('end_location').get('latitude'), vehicle.get('end_location').get('longitude')])
        routes_coords.append(route_coords)

    routes = []
    for route_coords in routes_coords:
        route, dists, times = await calculate_distances(route_coords)
        routes.append(route)

    return jsonify({'routes': routes})

@bp.route('/api/html_map', methods=['GET'])
async def get_html_map():

    """
    data format example:
    {
    "vehicles": [
        {
            'start_location': {},
            'end_location': {},
            'locations': [{}, {}],
        }
        ],
    }
    """

    data = request.get_json()

    if 'vehicles' not in data or not data['vehicles']:
        return jsonify({'error': 'No vehicles provided'}), 400
    
    vehicles = data.get('vehicles')
    routes_coords = []
    for vehicle in vehicles:
        route_coords = []
        start_location = vehicle.get('start_location')
        route_coords.append([start_location.get('latitude'), start_location.get('longitude')])
        for location in vehicle.get('locations'):
            route_coords.append([location.get('latitude'), location.get('longitude')])
        end_loc = vehicle.get('end_location')
        route_coords.append([end_loc.get('latitude'), end_loc.get('longitude')])
        routes_coords.append(route_coords)
    print(routes_coords)

    routes_to_print = []
    for route_coords in routes_coords:
        route, dists, times = await calculate_distances(route_coords)
        routes_to_print.append(route)

    create_map(routes_to_print)
    return jsonify({'message': 'Map created'})


def init_app(app):
    app.register_blueprint(bp)