import requests
import folium
import csv
from pymongo import MongoClient

# Replace with your Google Maps API key
google_maps_api_key = "your_google_maps_api_key"

# If garbled characters appear on the map, add &language=zh-CN to the request URL
google_maps_api_url = "https://maps.googleapis.com/maps/api/geocode/json?key=" + google_maps_api_key

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['LiteratureNetwork']
papers_collection = db['Papers']

# Create a map object
mymap = folium.Map(location=[0, 0], zoom_start=2)

# Create a list to store coordinate information
coordinates_list = []

# Initialize the counter
coordinates_count = 0

# Traverse each document
for entry in papers_collection.find().limit(7650):
    affiliation = entry.get("Affiliation", "")

    # Call Google Maps API to get geographic coordinates
    response = requests.get(google_maps_api_url, params={"address": affiliation})
    location_data = response.json()

    # Extract coordinate information
    if location_data["status"] == "OK":
        lat = location_data["results"][0]["geometry"]["location"]["lat"]
        lng = location_data["results"][0]["geometry"]["location"]["lng"]

        # Add the coordinates to the map
        folium.Marker([lat, lng], popup=affiliation).add_to(mymap)

        # Add coordinate information to the list
        coordinates_list.append({"affiliation": affiliation, "lat": lat, "lng": lng})

        # Update counter
        coordinates_count += 1
        print(f"Number of coordinates obtained: {coordinates_count}")

# Save the map as an HTML file
mymap.save("map_with_affiliations.html")
