import requests
import asyncio
import json
from pprint import pprint

from .node import Node

async def get_coordinates(node: Node) -> tuple[float, float]:
    if node.latitude and node.longitude:
        return node.latitude, node.longitude
    # Bing Maps API endpoint
    endpoint = "http://dev.virtualearth.net/REST/v1/Locations"
    
    # Your Bing Maps API key
    api_key = "Agg3Y0d4Y9AXCgHr7czdzqzmBzyk5GHVJeORQ3hqzdYlxvqA_SpywmgADpXJtJij"
    
    # Construct the request URL
    params = {
        'query': node.address,
        'key': api_key
    }
    
    # Make the HTTP GET request
    response = await asyncio.get_event_loop().run_in_executor(None, requests.get, endpoint, params)
    
    # Parse the JSON response
    data = response.json()
    
    # Extract the latitude and longitude
    if data['resourceSets'] and data['resourceSets'][0]['resources']:
        coordinates = data['resourceSets'][0]['resources'][0]['point']['coordinates']
        latitude = coordinates[0]
        longitude = coordinates[1]
        return latitude, longitude
    else:
        return None, None

    
def create_distance_matrix(coords: list) -> list:
    # Bing Maps API endpoint for distance matrix
    endpoint = "https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix"
    
    # Your Bing Maps key
    api_key = "Agg3Y0d4Y9AXCgHr7czdzqzmBzyk5GHVJeORQ3hqzdYlxvqA_SpywmgADpXJtJij"
    
    # Construct the request payload
    origins = [{"latitude": lat, "longitude": lon} for lat, lon in coords]
    destinations = [{"latitude": lat, "longitude": lon} for lat, lon in coords]
    
    payload = {
        "origins": origins,
        "destinations": destinations,
        "travelMode": "driving"
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Make the HTTP POST request
    response = requests.post(endpoint, params={'key': api_key}, headers=headers, data=json.dumps(payload))
    
    # Parse the JSON response
    data = response.json()
    pprint(data)
    if 'resourceSets' in data and data['resourceSets'][0]['resources']:
        resources = data['resourceSets'][0]['resources'][0]
        results = resources['results']
        size = len(coords)
        distance_matrix = [[0] * size for _ in range(size)]
        
        for result in results:
            origin_index = result['originIndex']
            destination_index = result['destinationIndex']
            distance_matrix[origin_index][destination_index] = int(result['travelDuration']) # distance in minutes
        return distance_matrix
    else:
        return None
    # if 'resourceSets' in data and data['resourceSets'][0]['resources']:
    #     resources = data['resourceSets'][0]['resources'][0]
    #     results = resources['results']
    #     size = len(coords)
    #     distance_matrix = [[0] * size for _ in range(size)]
        
    #     for result in results:
    #         origin_index = result['originIndex']
    #         destination_index = result['destinationIndex']
    #         distance_matrix[origin_index][destination_index] = int(result['travelDistance']*1000) # Convert to meters
        
    #     return distance_matrix
    # else:
    #     return None

async def calculate_distance(coord1: tuple, coord2: tuple):
    # Bing Maps API endpoint for route calculation
    endpoint = "https://dev.virtualearth.net/REST/v1/Routes"
    
    # Your Bing Maps key
    api_key = "Agg3Y0d4Y9AXCgHr7czdzqzmBzyk5GHVJeORQ3hqzdYlxvqA_SpywmgADpXJtJij"
    
    # Construct the request URL
    params = {
        'wayPoint.1': f'{coord1[0]},{coord1[1]}',
        'wayPoint.2': f'{coord2[0]},{coord2[1]}',
        'key': api_key,
        'distanceUnit': 'km',
        'routeAttributes': 'routePath'
    }
    
    # Make the HTTP GET request
    response = await asyncio.get_event_loop().run_in_executor(None, requests.get, endpoint, params)
    
    # Parse the JSON response
    data = response.json()
    
    # Extract the distance
    if 'resourceSets' in data and data['resourceSets'][0]['resources']:
        data = data['resourceSets'][0]['resources'][0]
        route = data['routePath']['line']['coordinates']
        distance = data['travelDistance']
        time = data['travelDuration'] / 60
        print(f'Distance: {distance} km, Time: {time} minutes')
        return route, distance, time
    else:
        return None

async def calculate_distances(coords: list) -> tuple[list, list]:

    results = await asyncio.gather(*[calculate_distance(loc1, loc2) for loc1, loc2 in zip(coords[:-1], coords[1:])])

    distances = []
    times = []
    routes = []
    for (route, dist, time) in results:
        distances.append(dist)
        routes.append(route)
        times.append(time)
    return routes, distances, times