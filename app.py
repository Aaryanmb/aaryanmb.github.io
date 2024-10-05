

import folium
import requests
from geopy.distance import geodesic
from IPython.display import display

# Function to fetch the route between multiple points using OpenRouteService API
def fetch_route(locations):
    # Define the API endpoint
    endpoint = 'https://api.openrouteservice.org/v2/directions/driving-car'

    # Define parameters
    params = {
        'api_key': '5b3ce3597851110001cf6248a5217a7238674955a7fc3b5c31d70a3e',  # Replace with your OpenRouteService API key
        'start': f'{locations[0][1]},{locations[0][0]}',  # Starting point (lon, lat)
        'end': f'{locations[-1][1]},{locations[-1][0]}',  # Ending point (lon, lat)
    }

    # Make a GET request to the API
    response = requests.get(endpoint, params=params)

    # Check for a successful response
    if response.status_code == 200:
        data = response.json()
        # Extract route coordinates from the response
        route_coordinates = data['features'][0]['geometry']['coordinates']
        # Reverse the coordinates for (lat, lon)
        return [(point[1], point[0]) for point in route_coordinates]
    else:
        print(f"Error fetching route: {response.status_code}, {response.text}")
        return []

# Function to place waypoints evenly along the route
def get_waypoints(route, num_waypoints=3):
    route_length = len(route)
    interval = route_length // (num_waypoints + 1)  # Divide the route into segments
    waypoints = [route[i * interval] for i in range(1, num_waypoints + 1)]  # Pick waypoints at equal intervals
    return waypoints

# Function to display the route on a map with multiple waypoints
def display_route(start, end):
    # Create map centered around starting point
    map_obj = folium.Map(location=start, zoom_start=14)  # Increased zoom for locality

    # Markers for start and end points
    truck_icon_url = 'https://th.bing.com/th/id/OIP.kF9fFDnJh2CZM34zCpDf8QHaEE?w=300&h=180&c=7&r=0&o=5&dpr=1.3&pid=1.7'  # Truck icon URL
    folium.Marker(location=start,
                  popup='Start',
                  icon=folium.CustomIcon(icon_image=truck_icon_url, icon_size=(30, 30))).add_to(map_obj)

    # Destination icon URL
    destination_icon_url = 'https://th.bing.com/th/id/OIP.e-AAfc2kjpWT3FW_rRg1ggHaHa?w=213&h=213&c=7&r=0&o=5&dpr=1.3&pid=1.7'  # Destination icon URL
    folium.Marker(location=end,
                  popup='End',
                  icon=folium.CustomIcon(icon_image=destination_icon_url, icon_size=(30, 30))).add_to(map_obj)

    # Fetch the complete route
    locations = [start, end]
    segment_route = fetch_route(locations)

    # Initialize total distance
    total_distance = 0

    # Draw the complete route if available
    if segment_route:
        folium.PolyLine(locations=segment_route, color='blue', weight=5, opacity=0.8).add_to(map_obj)

        # Calculate total distance
        for i in range(len(segment_route) - 1):
            total_distance += geodesic(segment_route[i], segment_route[i + 1]).kilometers

        # Display total distance on map
        midpoint = (segment_route[len(segment_route) // 2][0], segment_route[len(segment_route) // 2][1])  # Midpoint of the route
        folium.Marker(location=midpoint,
                      popup=f"Total Distance: {total_distance:.2f} km",
                      icon=folium.DivIcon(html=f'<div style="font-size: 12pt; color: blue;">Total Distance: {total_distance:.2f} km</div>')).add_to(map_obj)

        # Get evenly spaced waypoints along the route
        waypoints = get_waypoints(segment_route)

        # Add custom icons for the waypoints
        waypoint_icon_url = 'https://thumbs.dreamstime.com/b/destination-icon-blue-vector-circle-isolated-white-background-109233403.jpg'  # Waypoint icon URL
        for idx, waypoint in enumerate(waypoints, start=1):
            folium.Marker(location=waypoint,
                          popup=f'Waypoint {idx}',
                          icon=folium.CustomIcon(icon_image=waypoint_icon_url, icon_size=(30, 30))).add_to(map_obj)

    return map_obj, total_distance  # Return both the map and the total distance

# Example usage:
# Define start point (new coordinates)
current_location = (12.9342, 77.6170)  # Example starting point (Bangalore)

# Define end point (new coordinates)
destination = (12.97194000, 77.59369000)  # Example destination coordinates (Bangalore)

# Display route on map
route_map, total_distance = display_route(current_location, destination)

# Display map in the notebook
display(route_map)

# Print total distance outside the map
print(f"Total Distance: {total_distance:.2f} km")
