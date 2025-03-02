import folium

# Create a map centered at a specific location
m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

# Add a marker
folium.Marker(
    location=[40.7128, -74.0060],
    popup="New York City",
    tooltip="Click for more info"
).add_to(m)

# Display the map
m.save("simple_map.html")
m