import requests
import folium
import logging
import json
from datetime import time

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.conf import settings

from .forms import AddressForm, RouteParametersForm
from .models import AddressModel, VehicleModel, StartLocationModel, EndLocationModel, OptimisedLocation, OptimisedVehicle, OptimisedRoute, OptimisedStartLocation, OptimisedEndLocation

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'home.html')

def get_lat_long_from_bing(address):
    url = f"http://dev.virtualearth.net/REST/v1/Locations"
    params = {
        'query': address,
        'key': settings.BING_MAPS_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['resourceSets'] and data['resourceSets'][0]['resources']:
            coordinates = data['resourceSets'][0]['resources'][0]['point']['coordinates']
            return coordinates[0], coordinates[1]
    return None, None

def address_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    # try:
    #     if request.method == 'POST' and 'addressForm' in request.POST:
    #         print("Processing address form submission...")
    #         address_form = AddressForm(request.POST)
    #         if address_form.is_valid():
    #             cleaned_data = address_form.cleaned_data
    #             address = cleaned_data.get('address')
    #             latitude, longitude = get_lat_long_from_bing(address)
    #             if latitude is None or longitude is None:
    #                 return HttpResponse("Could not retrieve latitude and longitude for the address.", status=400)
    #             print(f"Address: {address}, Latitude: {latitude}, Longitude: {longitude}")
    #             # Save the address to the database
    #             AddressModel.objects.create(
    #                 user=request.user,
    #                 address=address,
    #                 latitude=latitude,
    #                 longitude=longitude)
                
    #             use_demand = request.GET.get('use_demand', 'off')
    #             use_time_window = request.GET.get('use_time_window', 'off')

    #             if request.headers.get('HX-Request'):
    #                 addresses = AddressModel.objects.filter(user=request.user)
    #                 address_form = AddressForm()
    #                 rendered_row = render_to_string('partials/address_row.html', {'addresses': addresses, 'use_demand': use_demand, 'use_time_window': use_time_window, "address_form": address_form})
    #                 return HttpResponse(rendered_row)

    #             return HttpResponse(f"Address submitted successfully! You entered: {address}")
    #     else:
    #         address_form = AddressForm()
    # except Exception as e:
    #     logger.error(f"Error processing request: {e}")
    #     return HttpResponse("An error occurred.", status=500)
    
    use_demand = request.GET.get('use_demand', 'off')
    use_time_window = request.GET.get('use_time_window', 'off')
    print(f"Use demand: {use_demand}, Use time window: {use_time_window}")
    
    address_form = AddressForm()
    
    route_form = RouteParametersForm()
    
    # address table
    addresses = AddressModel.objects.filter(user=request.user)

    # vehicle table
    vehicles = VehicleModel.objects.filter(user=request.user)

    start_location = StartLocationModel.objects.filter(user=request.user).first()
    if not start_location:
        print("No start location found. Creating default start location...")
        start_location = StartLocationModel.objects.create(
            user=request.user,
        )

    end_location = EndLocationModel.objects.filter(user=request.user).first()
    if not end_location:
        print("No end location found. Creating default start location...")
        end_location = EndLocationModel.objects.create(
            user=request.user,
        )

    # Render the map as HTML
    map_html = create_map(request)
    optimised_map_html = create_optimised_maps(request)
    return render(request, 'address_form.html', {
        'address_form': address_form,
        'addresses': addresses,
        'vehicles': vehicles,
        'start_location': start_location,
        'end_location': end_location,
        'map_html': map_html,
        'optimised_map_html': optimised_map_html,
        'route_form': route_form,
        'use_demand': use_demand,
        'use_time_window': use_time_window
        })

def _mins_to_time(minutes):
    print(minutes)
    if minutes is None or minutes < 0:
        raise ValueError("Minutes must be a positive integer")
    if minutes == 0:
        return time(hour=0, minute=0)
    print(f"Minutes: {minutes}")
    hours, minutes = divmod(minutes, 60)
    print(f"Hours: {hours}, Minutes: {minutes}")
    return time(hour=hours, minute=minutes)

def configure_optimised_route(request, data):
    headers = {
        'x-api-key': request.user.api_key
    }
    url = settings.UP_ROUTE_API_URL
    routes = requests.get(f"{url}api/route", json=data, headers=headers)
    if routes.status_code == 401:
        print(routes.json()['message'])
        return HttpResponse("Unauthorized request", status=401)
    routes = routes.json()['routes']
    optimised_route = OptimisedRoute.objects.create(
        user=request.user,
        total_duration=data['total_duration'],
        maximum_duration=data['max_duration'],
        total_demand=data['total_demand'],
        maximum_demand=data['max_demand'],
        total_stops=data['total_stops'],
        maximum_stops=data['max_stops'],
        latest_arrival=_mins_to_time(data['latest_arrival']),
        use_demand=data['use_demand'],
        use_time_window=data['use_time_windows']
    )
    print("Route created")
    for i, vehicle in enumerate(data['vehicles']):
        
        print(f'starting vehicle - vehicle')
        optimised_vehicle = OptimisedVehicle.objects.create(
            user=request.user,
            capacity=vehicle['capacity'],
            start_time=_mins_to_time(vehicle['start_time']),
            end_time=_mins_to_time(vehicle['end_time']),
            depart_time=_mins_to_time(vehicle['depart_time']),
            arrival_time=_mins_to_time(vehicle['arrival_time']),
            total_duration=vehicle['vehicle_duration'],
            total_demand=vehicle['vehicle_demand'],
            total_stops=vehicle['number_of_stops'],
            route=optimised_route
        )
        
        print(f'starting vehicle - start location')
        OptimisedStartLocation.objects.create(
            user=request.user,
            address=vehicle['start_location']['address'],
            latitude=vehicle['start_location']['latitude'],
            longitude=vehicle['start_location']['longitude'],
            depart_time=_mins_to_time(vehicle['start_location']['depart_time']),
            time_to_next=vehicle['start_location']['time_to_next_stop'],
            wait_time=vehicle['start_location']['wait_time'],
            demand=vehicle['start_location']['demand'],
            route_to_next=json.dumps(routes[i][0]),
            vehicle=optimised_vehicle
        )
        print(f'starting vehicle - end location')
        OptimisedEndLocation.objects.create(
            user=request.user,
            address=vehicle['end_location']['address'],
            latitude=vehicle['end_location']['latitude'],
            longitude=vehicle['end_location']['longitude'],
            arrival_time=_mins_to_time(vehicle['end_location']['arrival_time']),
            time_from_previous=vehicle['end_location']['time_from_previous_stop'],
            demand=vehicle['end_location']['demand'],
            vehicle=optimised_vehicle
        )
        for j, location in enumerate(vehicle['locations'], start=1):
            print(f'starting vehicle - location')
            OptimisedLocation.objects.create(
                user=request.user,
                address=location['address'],
                latitude=location['latitude'],
                longitude=location['longitude'],
                time_from_previous=location['time_from_previous_stop'],
                time_to_next=location['time_to_next_stop'],
                arrival_time=_mins_to_time(location['arrival_time']),
                depart_time=_mins_to_time(location['depart_time']),
                wait_time=location['wait_time'],
                demand=location['demand'],
                route_to_next=json.dumps(routes[i][j]),
                vehicle=optimised_vehicle
            )
            # optimised_vehicle.locations.add(optimised_location)
        # optimised_route.vehicles.add(optimised_vehicle)


def send_optimisation_request(request):
    print("Processing route settings form submission...")
    route_parameters_form = RouteParametersForm(request.POST)
    if route_parameters_form.is_valid():
        print("Form is valid")
        cleaned_data = route_parameters_form.cleaned_data
        use_demand = cleaned_data.get('use_demand')
        use_time_window = cleaned_data.get('use_time_window')
        print(cleaned_data)
    else:
        print("Form is invalid")
    
    vehicles = VehicleModel.objects.filter(user=request.user)
    print("Processing route settings form submission...")

    vehicles_dict = []
    for vehicle in vehicles:
        vehicle_dict = {}
        if use_time_window:
            vehicle_dict["start_time"] = vehicle.start_time.strftime('%H:%M'),
            vehicle_dict["end_time"] = vehicle.end_time.strftime('%H:%M')
        if use_demand:
            vehicle_dict["capacity"] = vehicle.capacity
        vehicles_dict.append(vehicle_dict)
    start_location = StartLocationModel.objects.filter(user=request.user).first()
    start_location_dict = {"address": start_location.address}
    end_location = EndLocationModel.objects.filter(user=request.user).first()
    end_location_dict = {"address": end_location.address}
    addresses = AddressModel.objects.filter(user=request.user)
    addresses_dict = []
    for address in addresses:
        address_obj = {'address': address.address}
        if use_demand:
            address_obj['demand'] = address.demand
        if use_time_window:
            address_obj['window_start'] = address.window_time_start.strftime('%H:%M')
            address_obj['window_end'] = address.window_time_end.strftime('%H:%M')
        addresses_dict.append(address_obj)
        print(address_obj)
    payload = {
        "vehicles": vehicles_dict,
        "start_location": start_location_dict,
        "end_location": end_location_dict,
        "locations": addresses_dict
    }
    # include user api_key in the header
    headers = {
        'x-api-key': request.user.api_key
    }
    # url1 = "http://127.0.0.1:5000/"
    # url2 = "http://192.168.0.20:5000/"
    # url3 = "https://uproute.app/api/"
    url = settings.UP_ROUTE_API_URL
    res = requests.post(f"{url}api/optimise_route", json=payload, headers=headers)
    if res.status_code == 401:
        print(res.json()['message'])
        return HttpResponse("Unauthorized request", status=401)
    if res.status_code == 200:
        configure_optimised_route(request, res.json())
        opt_map_html = create_optimised_maps(request)
        map_html = create_map(request)
        if request.headers.get('HX-Request'):
            rendered_row = render_to_string('partials/optimised_tab.html', {'optimised_map_html': opt_map_html, 'map_html': map_html})
            return HttpResponse(rendered_row)

def add_address(request):
    print(request.headers)
    address_form = AddressForm(request.POST)
    if address_form.is_valid():
        print("Address form is valid")
        cleaned_data = address_form.cleaned_data
        address = cleaned_data.get('address')
        latitude, longitude = get_lat_long_from_bing(address)
        print(f"Address: {address}, Latitude: {latitude}, Longitude: {longitude}")
        if latitude is None or longitude is None:
            return HttpResponse("Could not retrieve latitude and longitude for the address.", status=400)
        AddressModel.objects.create(
                user=request.user,
                address=address,
                latitude=latitude,
                longitude=longitude
                )
        
        return update_address_table(request)
            
def update_address_table(request):
    use_demand = request.GET.get('use_demand', 'off')
    use_time_window = request.GET.get('use_time_window', 'off')
    if request.headers.get('HX-Request'):
        addresses = AddressModel.objects.filter(user=request.user)
        address_form = AddressForm()
        rendered_row = render_to_string('partials/address_row.html', {'addresses': addresses, 'use_demand': use_demand, 'use_time_window': use_time_window, 'address_form': address_form})
        return HttpResponse(rendered_row)
    
def update_vehicle_table(request):
    use_demand = request.GET.get('use_demand', 'off')
    use_time_window = request.GET.get('use_time_window', 'off')
    if request.headers.get('HX-Request'):
        vehicles = VehicleModel.objects.filter(user=request.user)
        rendered_row = render_to_string('partials/vehicles_table.html', {'vehicles': vehicles, 'use_demand': use_demand, 'use_time_window': use_time_window})
        return HttpResponse(rendered_row)
    
def update_depot_table(request):
    use_demand = request.GET.get('use_demand', 'off')
    use_time_window = request.GET.get('use_time_window', 'off')
    print(f"Use demand: {use_demand}, Use time window: {use_time_window}")
    if request.headers.get('HX-Request'):
        start_location = StartLocationModel.objects.filter(user=request.user).first()
        end_location = EndLocationModel.objects.filter(user=request.user).first()
        rendered_row = render_to_string('partials/depot_table.html', {'start_location': start_location, 'end_location': end_location, 'use_demand': use_demand, 'use_time_window': use_time_window})
        return HttpResponse(rendered_row)

def delete_address(request, address_id):
    try:
        address = get_object_or_404(AddressModel, id=address_id)
        address.delete()
        if request.headers.get('HX-Request'):
            print("processing hx request")
            return HttpResponse()
        return HttpResponse("Address deleted successfully!")
    except Exception as e:
        logger.error(f"Error deleting address: {e}")
        return HttpResponse("An error occurred.", status=500)

def update_time_window(request, address_id):
    print(f"Updating time window for address ID: {address_id}")
    if request.method == 'POST':
        address = get_object_or_404(AddressModel, id=address_id)
        window_time_start = request.POST.get('window_time_start')
        window_time_end = request.POST.get('window_time_end')
        print(window_time_start, window_time_end)
        if window_time_start is not None:
            address.window_time_start = window_time_start
            address.save()
            print(address.window_time_start, address.window_time_end)
            print(type(address.window_time_start), type(address.window_time_end))
            return JsonResponse({'status': 'success', 'message': 'Time window updated successfully'})
        elif window_time_end is not None:
            address.window_time_end = window_time_end
            address.save()
            print(address.window_time_start, address.window_time_end)
            return JsonResponse({'status': 'success', 'message': 'Time window updated successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def update_demand(request, address_id):
    print(f"Updating demand for address ID: {address_id}")
    if request.method == 'POST':
        address = get_object_or_404(AddressModel, id=address_id)
        new_demand = request.POST.get('demand')
        print(new_demand)
        if new_demand is not None:
            address.demand = new_demand
            address.save()
            return JsonResponse({'status': 'success', 'message': 'Demand updated successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def add_vehicle(request):
    if request.method == 'POST':
        VehicleModel.objects.create(
            user=request.user,
        )
        if request.headers.get('HX-Request'):
            vehicles = VehicleModel.objects.filter(user=request.user)
            rendered_row = render_to_string('partials/vehicles_table.html', {'vehicles': vehicles})
            return HttpResponse(rendered_row)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def delete_vehicle(request, vehicle_id):
    print(f"Deleting vehicle ID: {vehicle_id}")
    try:
        vehicle = get_object_or_404(VehicleModel, id=vehicle_id)
        vehicle.delete()
        if request.headers.get('HX-Request'):
            print("processing hx request")
            return HttpResponse()
        return HttpResponse("Vehicle deleted successfully!")
    except Exception as e:
        logger.error(f"Error deleting vehicle: {e}")
        return HttpResponse("An error occurred.", status=500)

def update_vehicle_time_window(request, vehicle_id):
    print(f"Updating time window for vehicle ID: {vehicle_id}")
    if request.method == 'POST':
        vehicle = get_object_or_404(VehicleModel, id=vehicle_id)
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        print(start_time, end_time)
        if start_time is not None:
            vehicle.start_time = start_time
            vehicle.save()
            print(vehicle.start_time, vehicle.end_time)
            print(type(vehicle.start_time), type(vehicle.end_time))
            return JsonResponse({'status': 'success', 'message': 'Time window updated successfully'})
        elif end_time is not None:
            vehicle.end_time = end_time
            vehicle.save()
            print(vehicle.start_time, vehicle.end_time)
            return JsonResponse({'status': 'success', 'message': 'Time window updated successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def update_start_location_time_window(request, location_id):
    print(f"Updating time window for start location ID: {location_id}")
    if request.method == 'POST':
        location = get_object_or_404(StartLocationModel, id=location_id)
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        print(start_time, end_time)
        if start_time is not None:
            location.start_time = start_time
            location.save()
            print(location.start_time, location.end_time)
            print(type(location.start_time), type(location.end_time))
            return JsonResponse({'status': 'success', 'message': 'Time window updated successfully'})
        elif end_time is not None:
            location.end_time = end_time
            location.save()
            print(location.start_time, location.end_time)
            return JsonResponse({'status': 'success', 'message': 'Time window updated successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def update_end_location_time_window(request, location_id):
    print(f"Updating time window for end location ID: {location_id}")
    if request.method == 'POST':
        location = get_object_or_404(EndLocationModel, id=location_id)
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        print(start_time, end_time)
        if start_time is not None:
            location.start_time = start_time
            location.save()
            print(location.start_time, location.end_time)
            print(type(location.start_time), type(location.end_time))
            return JsonResponse({'status': 'success', 'message': 'Time window updated successfully'})
        elif end_time is not None:
            location.end_time = end_time
            location.save()
            print(location.start_time, location.end_time)
            return JsonResponse({'status': 'success', 'message': 'Time window updated successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def update_start_address(request, address_id):
    print(f"Updating start address for address ID: {address_id}")
    if request.method == 'POST':
        address = get_object_or_404(StartLocationModel, id=address_id)
        new_address = request.POST.get('address')
        latitude, longitude = get_lat_long_from_bing(address=new_address)
        if latitude is None or longitude is None:
            return HttpResponse("Could not retrieve latitude and longitude for the address.", status=400)
        print(f"Address: {new_address}, Latitude: {latitude}, Longitude: {longitude}")
        if new_address is not None:
            address.address = new_address
            address.latitude = latitude
            address.longitude = longitude
            address.save()
            return JsonResponse({'status': 'success', 'message': 'Address updated successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def update_end_address(request, address_id):
    print(f"Updating end address for address ID: {address_id}")
    if request.method == 'POST':
        address = get_object_or_404(EndLocationModel, id=address_id)
        new_address = request.POST.get('address')
        latitude, longitude = get_lat_long_from_bing(address=new_address)
        # if latitude is None or longitude is None:
        #     return HttpResponse("Could not retrieve latitude and longitude for the address.", status=400)
        print(f"Address: {new_address}, Latitude: {latitude}, Longitude: {longitude}")
        if new_address is not None:
            address.address = new_address
            address.latitude = latitude
            address.longitude = longitude
            address.save()
            return JsonResponse({'status': 'success', 'message': 'Address updated successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def update_capacity(request, vehicle_id):
    print(f"Updating Capacity for address ID: {vehicle_id}")
    if request.method == 'POST':
        vehicle = get_object_or_404(VehicleModel, id=vehicle_id)
        new_capacity = request.POST.get('capacity')
        print(new_capacity)
        if new_capacity is not None:
            vehicle.capacity = new_capacity
            vehicle.save()
            return JsonResponse({'status': 'success', 'message': 'Capacity updated successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def get_map(request):
    map_html = create_map(request)
    return JsonResponse({"map_html": map_html})

def get_first_valid_location(*locations) -> AddressModel:
    for location in locations:
        if location.latitude and location.longitude:
            return location
    return None

def create_map(request):
    
    print("creating setup map")
    start_location = StartLocationModel.objects.filter(user=request.user).first()
    addresses = AddressModel.objects.filter(user=request.user)
    end_location = EndLocationModel.objects.filter(user=request.user).first()

    first_location = get_first_valid_location(start_location, *addresses, end_location)
    # Create a Folium map centered on the first address
    if first_location:
        map_center = [first_location.latitude, first_location.longitude]
        zoom_start = 12
    else:
        map_center = [54.09884262, -2.98163056]  # Default center if no addresses
        zoom_start = 6
    folium_map = folium.Map(location=map_center, zoom_start=zoom_start)


    if start_location and start_location.latitude and start_location.longitude:
        folium.Marker(
            location=[start_location.latitude, start_location.longitude],
            popup=start_location.address,
            icon=folium.Icon(color='green')
        ).add_to(folium_map)

    if end_location and end_location.latitude and end_location.longitude:
        folium.Marker(
            location=[end_location.latitude, end_location.longitude],
            popup=end_location.address,
            icon=folium.Icon(color='red')
        ).add_to(folium_map)

    for address in addresses:
        if address.latitude and address.longitude:
            folium.Marker(
                location=[address.latitude, address.longitude],
                popup=address.address
            ).add_to(folium_map)

    return folium_map._repr_html_()

def create_optimised_maps(request):
    optimised_routes_for_html = []
    optimised_routes = OptimisedRoute.objects.filter(user=request.user)
    for optimised_route in optimised_routes:
        optimised_routes_for_html.append(create_optimised_map(request, optimised_route))
    return optimised_routes_for_html

def create_optimised_map(request, optimised_route):
    
    print(f"creating map for {optimised_route}")

    vehicles = OptimisedVehicle.objects.filter(route=optimised_route, user=request.user)
    user_locations = OptimisedLocation.objects.filter(user=request.user)
    start_locations = OptimisedStartLocation.objects.filter(user=request.user)
    end_locations = OptimisedEndLocation.objects.filter(user=request.user)

    first_vehicle = vehicles.first()
    if first_vehicle:
        start_location = start_locations.filter(vehicle=first_vehicle).first()
        map_center = [start_location.latitude, start_location.longitude]
        zoom_start = 12
    else:
        map_center = [54.09884262, -2.98163056]  # Default center if no vehicles
        zoom_start = 6

    colors = ['blue', 'purple', 'orange', 'darkred', 'cadetblue']
    optimised_map = folium.Map(location=map_center, zoom_start=zoom_start)

    for i, vehicle in enumerate(vehicles):
        color = colors[i % len(colors)]
        start_location = start_locations.filter(vehicle=vehicle).first()
        folium.Marker(
            location=[start_location.latitude, start_location.longitude],
            popup=start_location.address,
            icon=folium.Icon(color='green')
        ).add_to(optimised_map)
        route_path = json.loads(start_location.route_to_next)
        folium.PolyLine(route_path, color=color, weight=2.5, opacity=1).add_to(optimised_map)

        end_location = end_locations.filter(vehicle=vehicle).first()
        folium.Marker(
            location=[end_location.latitude, end_location.longitude],
            popup=end_location.address,
            icon=folium.Icon(color='red')
        ).add_to(optimised_map)

        locations = user_locations.filter(vehicle=vehicle)
        for location in locations:
            folium.Marker(
                location=[location.latitude, location.longitude],
                popup=location.address,
                icon=folium.Icon(color=color)
            ).add_to(optimised_map)
            route_path = json.loads(location.route_to_next)
            folium.PolyLine(route_path, color=color, weight=2.5, opacity=1).add_to(optimised_map)

    map_html = optimised_map._repr_html_()
    map_html, optimised_route, vehicles, start_locations, end_locations, user_locations
    return {
        'map_html': map_html,
        'optimised_route': optimised_route,
        'vehicles': vehicles,
        'start_locations': start_locations,
        'end_locations': end_locations,
        'user_locations': user_locations
        }

def delete_optimised_route(request, route_id):
    print(f"Deleting route ID: {route_id}")
    try:
        route = get_object_or_404(OptimisedRoute, id=route_id)
        print("Deleting route", route)
        route.delete()
        opt_map_html = create_optimised_maps(request)
        map_html = create_map(request)
        if request.headers.get('HX-Request'):
            rendered_row = render_to_string('partials/optimised_tab.html', {'optimised_map_html': opt_map_html, 'map_html': map_html})
            print("sedning response")
            return HttpResponse(rendered_row)
        return HttpResponse("Route deleted successfully!")
    except Exception as e:
        logger.error(f"Error deleting route: {e}")
        return HttpResponse("An error occurred.", status=500)