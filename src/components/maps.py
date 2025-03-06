# src/components/maps.py

import folium
from streamlit_folium import st_folium
import pandas as pd
import json
import os

def display_area_map(bbox: list[float]):
    """Display a map with the selected area."""
    center_lat = (bbox[1] + bbox[3]) / 2
    center_lon = (bbox[0] + bbox[2]) / 2
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=8)
    
    # Draw rectangle for bounding box
    folium.Rectangle(
        bounds=[[bbox[1], bbox[0]], [bbox[3], bbox[2]]],
        color="red",
        fill=True,
        popup="Search Area"
    ).add_to(m)

    # File paths
    cities_path = "src/data/us_cities.csv"
    regions_path = "src/data/us_regions.geojson"
    
     # Add US regions if file exists
    if os.path.exists(regions_path):
        with open(regions_path) as f:
            regions_data = json.load(f)
        folium.GeoJson(
            regions_data,
            name="US Regions"
        ).add_to(m)
    
    # Add cities if file exists
    if os.path.exists(cities_path):
        cities_df = pd.read_csv(cities_path)
        
        # Define a color mapping for regions
        region_colors = {
            'Northeast': 'blue',
            'Midwest': 'green',
            'South': 'red',
            'West': 'purple'
        }
        
        # Add city markers
        for _, city in cities_df.iterrows():
            icon = folium.Icon(
                icon="map-marker", 
                prefix="fa",
                color=region_colors.get(city.get('region'), 'gray')
            )
            
            folium.Marker(
                location=[city['latitude'], city['longitude']],
                popup=city.get('name', 'Unknown'),
                icon=icon
            ).add_to(m)
            
        # Add a legend
        legend_html = '''
            <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px">
            <p><strong>Regions</strong></p>
        '''
        
        for region, color in region_colors.items():
            legend_html += f'<p><i style="background:{color};width:10px;height:10px;display:inline-block"></i> {region}</p>'
        
        legend_html += '</div>'
        m.get_root().html.add_child(folium.Element(legend_html))

    return m