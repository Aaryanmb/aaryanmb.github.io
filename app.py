from flask import Flask, render_template, request
import folium
import requests
from geopy.distance import geodesic

app = Flask(__name__)

# Function to fetch the route between multiple points using OpenRouteService API
def fetch_route(locations):
    endpoint = 'https://api.openrouteservice.org/v2/directions/driving-car'
    params = {
        'api_key': '5b3ce3597851110001cf6248a5217a7238674955a7fc3b5c31d70a3e',
        'start': f'{locations[0][1]},{locations[0][0]}',
        'end': f'{locations[-1][1]},{locations[-1][0]}',
    }
    response = requests.get(endpoint, params=params)

    if response.status_code == 200:
        data = response.json()
        route_coordinates = data['features'][0]['geometry']['coordinates']
        return [(point[1], point[0]) for point in route_coordinates]
    else:
        print(f"Error fetching route: {response.status_code}, {response.text}")
        return []

# Function to place waypoints evenly along the route
def get_waypoints(route, num_waypoints=3):
    route_length = len(route)
    interval = route_length // (num_waypoints + 1)
    waypoints = [route[i * interval] for i in range(1, num_waypoints + 1)]
    return waypoints

# Function to generate map with the route and waypoints
def generate_map(start, end, waypoints_count=3):
    map_obj = folium.Map(location=start, zoom_start=14)

    # Truck icon
    truck_icon_url = 'https://th.bing.com/th/id/OIP.kF9fFDnJh2CZM34zCpDf8QHaEE?w=300&h=180&c=7&r=0&o=5&dpr=1.3&pid=1.7'
    folium.Marker(location=start, popup='Start', icon=folium.CustomIcon(truck_icon_url, icon_size=(30, 30))).add_to(map_obj)
    
    # Destination icon
    destination_icon_url = 'https://th.bing.com/th/id/OIP.e-AAfc2kjpWT3FW_rRg1ggHaHa?w=213&h=213&c=7&r=0&o=5&dpr=1.3&pid=1.7'
    folium.Marker(location=end, popup='End', icon=folium.CustomIcon(destination_icon_url, icon_size=(30, 30))).add_to(map_obj)
    
    # Fetch route
    locations = [start, end]
    segment_route = fetch_route(locations)

    total_distance = 0

    if segment_route:
        folium.PolyLine(locations=segment_route, color='blue', weight=5, opacity=0.8).add_to(map_obj)

        for i in range(len(segment_route) - 1):
            total_distance += geodesic(segment_route[i], segment_route[i + 1]).kilometers

        waypoints = get_waypoints(segment_route, waypoints_count)

        # Waypoint icon
        waypoint_icon_url = 'https://thumbs.dreamstime.com/b/destination-icon-blue-vector-circle-isolated-white-background-109233403.jpg'
        for idx, waypoint in enumerate(waypoints, start=1):
            folium.Marker(location=waypoint, popup=f'Waypoint {idx}', icon=folium.CustomIcon(waypoint_icon_url, icon_size=(30, 30))).add_to(map_obj)

    return map_obj, total_distance

@app.route('/', methods=['GET', 'POST'])
def index():
    map_html = None
    total_distance = 0

    if request.method == 'POST':
        try:
            start_lat = float(request.form['start_lat'])
            start_lon = float(request.form['start_lon'])
            end_lat = float(request.form['end_lat'])
            end_lon = float(request.form['end_lon'])
            waypoints = int(request.form['waypoints'])

            start = (start_lat, start_lon)
            end = (end_lat, end_lon)

            route_map, total_distance = generate_map(start, end, waypoints)
            map_html = route_map._repr_html_()  # Get map as HTML
        except Exception as e:
            print(f"Error: {e}")

    return render_template('index.html', map_html=map_html, total_distance=total_distance)

if __name__ == '__main__':
    app.run(debug=True)
