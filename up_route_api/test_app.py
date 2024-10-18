import httpx 


def test_home():
    with httpx.Client() as client:
        response = client.get('http://192.168.0.20:5000/test')
        assert response.status_code == 200
        assert response.json() == {"message": "ping"}

# def test_invalid_route():
#     with httpx.Client() as client:
#         response = client.post('http://127.0.0.1:5000/optimise_route', json={
#             'locations': []
#         })
#         assert response.status_code == 400
#         assert response.json() == {"error": "No locations provided"}

# def test_non_string_addresses():
#     with httpx.Client() as client:
#         response = client.post('http://127.0.0.1:5000/optimise_route', json={
#             'addresses': [
#                 123,  # Invalid address
#                 "20 North Bridge, Edinburgh EH1 1TR, United Kingdom",  # Valid address
#             ]
#         })
#         assert response.status_code == 400
#         assert response.json() == {"error": "All addresses must be strings"}

# def test_optimize_route_with_capacity():

#     locations = [
#             {"address": "20 North Bridge, Edinburgh EH1 1TR, United Kingdom", "demand": 5},  # The Scotsman Hotel
#             {"address": "11 Blythswood Square, Glasgow G2 4AD, United Kingdom", "demand": 8},  # Kimpton Blythswood Square Hotel
#             {"address": "Auchterarder, Perthshire PH3 1NF, United Kingdom", "demand": 12},  # The Gleneagles Hotel
#             # {"address": "19-21 George St, Edinburgh EH2 2PB, United Kingdom", "demand": 6},  # The Principal Edinburgh George Street
#             # {"address": "Loch Lomond, Alexandria G83 8QZ, United Kingdom", "demand": 4},  # Cameron House on Loch Lomond
#             # {"address": "Old Station Rd, St Andrews KY16 9SP, United Kingdom", "demand": 7},  # Old Course Hotel
#             # {"address": "1 Festival Square, Edinburgh EH3 9SR, United Kingdom", "demand": 9},  # Sheraton Grand Hotel & Spa
#             # {"address": "301 Argyle St, Glasgow G2 8DL, United Kingdom", "demand": 3},  # Radisson Blu Hotel, Glasgow
#             # {"address": "St Andrews KY16 8PN, United Kingdom", "demand": 11}  # Fairmont St Andrews
#             ]
    
#     vehicles = [
#         {"capacity": 15},
#         {"capacity": 10},
#         {"capacity": 12}
#     ]
#     start_location = {"address": "1 Princes St, Edinburgh EH2 2EQ, United Kingdom"}  # The Balmoral Hotel

#     payload = {
#         'locations': locations,
#         'vehicles': vehicles,
#         'start_location': start_location
#     }

#     with httpx.Client() as client:
#         response = client.post('http://127.0.0.1:5000/optimise_route', json=payload)
#         assert response.status_code == 200
#         assert "optimised_routes" in response.json()

def test_optimize_route_with_time_windows():
    locations = [
        {
            "address": "20 North Bridge, Edinburgh EH1 1TR, United Kingdom",
            # "demand": 5,
            "window_start": "09:00",
            "window_end": "17:00"
        },  # The Scotsman Hotel
        {
            "address": "11 Blythswood Square, Glasgow G2 4AD, United Kingdom",
            # "demand": 8,
            "window_start": "09:00",
            "window_end": "17:30"
        },  # Kimpton Blythswood Square Hotel
        {
            "address": "Auchterarder, Perthshire PH3 1NF, United Kingdom",
            # "demand": 12,
            "window_start": "09:00",
            "window_end": "17:00"
        },  # The Gleneagles Hotel
        # {"address": "19-21 George St, Edinburgh EH2 2PB, United Kingdom", "demand": 6},  # The Principal Edinburgh George Street
        # {"address": "Loch Lomond, Alexandria G83 8QZ, United Kingdom", "demand": 4},  # Cameron House on Loch Lomond
        # {"address": "Old Station Rd, St Andrews KY16 9SP, United Kingdom", "demand": 7},  # Old Course Hotel
        # {"address": "1 Festival Square, Edinburgh EH3 9SR, United Kingdom", "demand": 9},  # Sheraton Grand Hotel & Spa
        # {"address": "301 Argyle St, Glasgow G2 8DL, United Kingdom", "demand": 3},  # Radisson Blu Hotel, Glasgow
        # {"address": "St Andrews KY16 8PN, United Kingdom", "demand": 11}  # Fairmont St Andrews
    ]
    
    vehicles = [
        {"capacity": 15, "start_time": "08:00", "end_time": "17:00"},
        {"capacity": 10, "start_time": "09:00", "end_time": "18:00"},
        {"capacity": 12, "start_time": "09:00", "end_time": "19:00"}
    ]
    start_location = {
        "address": "1 Princes St, Edinburgh EH2 2EQ, United Kingdom",
        "window_start": "08:00",
        "window_end": "19:00"
        }  # The Balmoral Hotel

    payload = {
        'locations': locations,
        'vehicles': vehicles,
        'start_location': start_location
    }

    with httpx.Client() as client:
        response = client.post('http://192.168.0.20:5000/optimise_route', json=payload, timeout=30)
        assert response.status_code == 200
        assert "max_duration" in response.json()
        assert "total_demand" in response.json()
        assert "total_duration" in response.json()
        assert "max_demand" in response.json()
        assert "vehicles" in response.json()
        assert "latest_arrival" in response.json()

        data = response.json()
        assert len(data["vehicles"]) == len(vehicles)
