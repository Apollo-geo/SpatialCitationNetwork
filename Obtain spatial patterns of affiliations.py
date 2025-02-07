import folium
import pandas as pd
from pymongo import MongoClient
from bson import ObjectId

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['LiteratureNetwork']
papers_collection = db['Papers']
references_collection = db['References']

# Create a Folium map
m = folium.Map(location=[0, 0], zoom_start=3)

# Dictionary storing article location information
locations = {}

# Add article location marker
for paper in papers_collection.find():
    title = paper['Title']
    lat = paper.get('Latitude', 0)
    lng = paper.get('Longitude', 0)
    Affi = paper.get('Affiliation', None)

    # Check if there is latitude and longitude information
    if Affi is not None:
        # Create a small icon
        small_icon = folium.Icon(icon_size=(1, 1))

        #Mark the article location on the map and apply a custom icon style
        folium.Marker([lat, lng], popup=title, icon=small_icon).add_to(m)

        #Store article location information
        locations[title] = {'lat': lat, 'lng': lng}

# Add reference relationship line
for reference in references_collection.find():
    source_title = reference.get('PaperTitle', '')
    source_location = locations.get(str(source_title), {})  # 确保 source_title 是字符串

    if source_location:
        for ref in reference.get('References', []):
            target_title = ref.get('Title', '')
            target_location = locations.get(str(target_title), {})  # 确保 target_title 是字符串

            if target_location:
                # Connect references on the map
                folium.PolyLine([(source_location['lat'], source_location['lng']),
                                  (target_location['lat'], target_location['lng'])],
                                 color='blue', weight=0.1).add_to(m)

# Save the map as an HTML file
m.save('map_with_reference_weight001v4.html')

# Close MongoDB connection
client.close()