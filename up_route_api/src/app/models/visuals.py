import folium

def add_route_to_map(route: dict, map: folium.Map, color: str = 'blue'):
    # Initialize the map centered on the start of the route
    
    for address in route:
        # generate the coordinated from the route
        coords = address['routeLegs'][0]['actualStart']['coordinates']
        folium.Marker(location=coords).add_to(map)

    
    # Add markers for the start and end points
    start_coords = route[0]['routeLegs'][0]['actualStart']['coordinates']
    folium.Marker(location=start_coords, popup='Start').add_to(map)
    end_coords = route[-1]['routeLegs'][0]['actualEnd']['coordinates']
    folium.Marker(location=end_coords, popup='End').add_to(map)
    
    # Extract the route path
    route_path = [section['routePath']['line']['coordinates'] for section in route]
    
    # Draw the route on the map
    folium.PolyLine(route_path, color=color, weight=2.5, opacity=1).add_to(map)
    

def create_map(routes: dict, output_file: str = 'route_map.html'):
    # Initialize the map centered on the start of the route
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
    start_coords = routes[0][0]['routeLegs'][0]['actualStart']['coordinates']
    m = folium.Map(location=start_coords, zoom_start=10)

    for i, route in enumerate(routes):
        color = colors[i % len(colors)]
        add_route_to_map(route, m, color)
    
    # Save the map to an HTML file
    m.save(output_file)