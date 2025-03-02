import streamlit as st
import openai
from openai import OpenAI
from pystac_client import Client
from geopy.geocoders import Nominatim
import pycountry
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import folium
from streamlit_folium import st_folium
import rioxarray
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import planetary_computer
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
import requests
from io import BytesIO

# Load environment variables
load_dotenv()
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
# Configure the page to use wide mode by default
st.set_page_config(layout="wide")

# Add this near the top of the file after imports
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False
    st.session_state.search_results = None
    st.session_state.location_name = None
    st.session_state.bbox = None
    st.session_state.collection = None
    st.session_state.collection_info = None
    st.session_state.report = None
    st.session_state.selected_collection = None
    st.session_state.visualization_data = None
    st.session_state.item_info = None
    st.session_state.analysis_results = None

# Function to check if two bounding boxes intersect
def bbox_intersects(spatial_extent, bbox_filter):
    # spatial_extent and bbox_filter are in the format [min_lon, min_lat, max_lon, max_lat]
    min_lon1, min_lat1, max_lon1, max_lat1 = spatial_extent
    min_lon2, min_lat2, max_lon2, max_lat2 = bbox_filter

    # Check if the bounding boxes intersect
    return not (min_lon1 > max_lon2 or max_lon1 < min_lon2 or min_lat1 > max_lat2 or max_lat1 < min_lat2)

# Helper function to parse dates and ensure they are offset-aware
def parse_date(date):
    if isinstance(date, datetime):  # If already a datetime object
        return date if date.tzinfo else date.replace(tzinfo=timezone.utc)  # Make offset-aware
    if isinstance(date, str):  # If it's a string, parse it
        dt = datetime.fromisoformat(date)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)  # Make offset-aware
    return None  # If None or invalid, return None

# Function to check if two temporal intervals intersect
def temporal_intersects(temporal_extent, temporal_filter):
    # temporal_extent is in format datetime objects
    # temporal_filter is in the string format ["2020-01-01", "2023-01-01"]
    start_date1, end_date1 = temporal_extent
    start_date2, end_date2 = [parse_date(date) for date in temporal_filter]

    # Check if the temporal intervals intersect
    # Check for intersection
    if (end_date1 is not None and start_date2 is not None and end_date1 < start_date2) or \
       (start_date1 is not None and end_date2 is not None and start_date1 > end_date2):
        return False  # No intersection
    return True  # Intersecting

# Function to generate text using OpenAI ChatCompletion
def generate_text(prompt):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a geospatial data expert and good at ESG research."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating text: {str(e)}")
        return None

# Function to get bounding box for a location
def get_bounding_box(location):
    try:
        geolocator = Nominatim(user_agent="stac_search_app")
        loc = geolocator.geocode(location)
        
        if loc:
            # Create a bounding box with a more reasonable size
            # For cities, we'll use approximately 50km radius (roughly 0.5 degrees)
            buffer = 0.5
            return [
                loc.longitude - buffer,
                loc.latitude - buffer,
                loc.longitude + buffer,
                loc.latitude + buffer
            ]
        else:
            return None
    except Exception as e:
        st.error(f"Error getting location: {str(e)}")
        return None
    
def display_area_map(bbox):
    """Display a map with the selected area"""
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
    
    return m

# NEW FUNCTIONS FOR DATA ACCESS AND VISUALIZATION

# Function to search for items within a collection
def search_stac_items(client, collection_id, bbox, time_range):
    """Search for STAC items within a specific collection and filters"""
    search = client.search(
        collections=[collection_id],
        bbox=bbox,
        datetime=time_range
    )
    return list(search.items())

# Function to get the actual data from an asset
def get_asset_data(item, asset_key):
    """Get the data from a specific asset of a STAC item"""
    asset = item.assets[asset_key]
    
    # Sign the URL if using Planetary Computer
    signed_url = planetary_computer.sign(asset.href)
    
    # For cloud-optimized GeoTIFFs
    if asset.media_type in ["image/tiff", "image/x.geotiff", "image/tiff; application=geotiff"]:
        return rioxarray.open_rasterio(signed_url)
    
    # For NetCDF data
    elif asset.media_type in ["application/x-netcdf", "application/netcdf"]:
        return xr.open_dataset(signed_url)
    
    # For vector data (GeoJSON)
    elif asset.media_type == "application/geo+json":
        response = requests.get(signed_url)
        return gpd.read_file(BytesIO(response.content))
    
    # For CSV data
    elif asset.media_type == "text/csv":
        return pd.read_csv(signed_url)
    
    else:
        raise ValueError(f"Unsupported media type: {asset.media_type}")

# Function to visualize raster data on a map
def visualize_raster_on_map(data, bbox, colormap='viridis', layer_name="Raster Layer"):
    """Visualize a raster dataset on a folium map"""
    center_lat = (bbox[1] + bbox[3]) / 2
    center_lon = (bbox[0] + bbox[2]) / 2
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=8)
    
    # Draw rectangle for bounding box
    folium.Rectangle(
        bounds=[[bbox[1], bbox[0]], [bbox[3], bbox[2]]],
        color="red",
        fill=False,
        popup="Search Area"
    ).add_to(m)
    
    # Create a temporary image file to display on the map
    fig, ax = plt.subplots(figsize=(10, 10))
    data.plot(ax=ax, cmap=colormap)
    plt.axis('off')
    
    # Save as base64 image and add to the map
    img_path = "temp_raster.png"
    plt.savefig(img_path, bbox_inches='tight', pad_inches=0)
    
    # Add the image as an overlay
    img_bounds = [[bbox[1], bbox[0]], [bbox[3], bbox[2]]]
    folium.raster_layers.ImageOverlay(
        image=img_path,
        bounds=img_bounds,
        opacity=0.7,
        name=layer_name
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

# Function to analyze data for ESG insights
def analyze_for_esg(data, collection_id, location_name):
    """Perform basic analysis on the data with ESG context"""
    results = {}
    
    if isinstance(data, xr.DataArray) or isinstance(data, xr.Dataset):
        # For raster data
        if isinstance(data, xr.DataArray):
            # Get basic statistics
            results["min"] = float(data.min().values)
            results["max"] = float(data.max().values)
            results["mean"] = float(data.mean().values)
            
            # Calculate additional metrics based on collection type
            if "landcover" in collection_id.lower():
                # Simple land cover classification analysis
                unique_values, counts = np.unique(data.values, return_counts=True)
                results["land_cover_distribution"] = {int(val): int(count) for val, count in zip(unique_values, counts)}
                
            elif "temperature" in collection_id.lower():
                # Temperature trend analysis
                if "time" in data.dims:
                    trend = data.groupby("time").mean().values
                    results["temperature_trend"] = trend.tolist()
    
    elif isinstance(data, gpd.GeoDataFrame):
        # For vector data
        results["feature_count"] = len(data)
        
        # Get column statistics for numeric columns
        for col in data.select_dtypes(include=['number']).columns:
            if col != data.geometry.name:
                results[f"{col}_mean"] = data[col].mean()
                results[f"{col}_min"] = data[col].min()
                results[f"{col}_max"] = data[col].max()
    
    return results

# Main function to access and visualize data from a collection
def access_and_visualize_data(collection_id, bbox, temporal_filter, location_name):
    """Access and visualize data from a STAC collection"""
    
    # Connect to the STAC API
    stac_url = "https://planetarycomputer.microsoft.com/api/stac/v1"
    client = Client.open(stac_url)
    
    # Search for items
    items = search_stac_items(client, collection_id, bbox, temporal_filter)
    st.write("items:",items)
    
    if not items:
        return None, None, f"No items found for collection {collection_id} in the specified area and time range."
    
    # Get the first item for demonstration
    item = items[0]
    st.write("item0:",item)
    
    # Display item information
    item_info = {
        "id": item.id,
        "datetime": item.datetime.isoformat() if item.datetime else "Unknown",
        "assets": list(item.assets.keys())
    }
    
    # Determine which asset to use (depends on the collection)
    # This requires knowledge of the specific collection
    available_assets = list(item.assets.keys())
    
    # Try to pick a good asset based on common naming conventions
    asset_key = None
    priority_assets = ["visual", "data", "image", "cog", "geotiff", "analytic", "B04", "red"]
    
    for priority in priority_assets:
        matching_assets = [a for a in available_assets if priority.lower() in a.lower()]
        if matching_assets:
            asset_key = matching_assets[0]
            break
    
    # If no priority asset is found, use the first available asset
    if not asset_key and available_assets:
        asset_key = available_assets[0]
    
    if not asset_key:
        return None, item_info, "No suitable assets found in the item."
    
    try:
        # Get the data
        data = get_asset_data(item, asset_key)
        
        # Analyze the data for ESG insights
        analysis_results = analyze_for_esg(data, collection_id, location_name)
        
        # Visualize the data if it's a raster
        if isinstance(data, xr.DataArray):
            map_obj = visualize_raster_on_map(data, bbox, layer_name=f"{collection_id} - {asset_key}")
            return map_obj, item_info, analysis_results
        else:
            # For non-raster data, return the data for other visualizations
            return data, item_info, analysis_results
            
    except Exception as e:
        return None, item_info, f"Error accessing data: {str(e)}"

# Streamlit UI
st.title("Inspect Geospatial Data for ESG")
st.sidebar.header("Filters")

# Replace the bbox_filter input with address input
location = st.sidebar.text_input("Location (e.g., 'New York City' or 'Tokyo, Japan')", "New York City")
# set temporal_filter a global variable
temporal_filter = st.sidebar.text_input("Date Range (comma-separated)", "2020-01-01, 2025-12-31")
# st.write(temporal_filter.split(", "),"/".join(temporal_filter),"/".join(temporal_filter.split(", ")))

if st.sidebar.button("Search and Generate Data insights"):
    # Get bounding box from location
    bbox_filter = get_bounding_box(location)
    
    if bbox_filter is None:
        st.error("Could not find the specified location. Please try a different location name.")
        st.session_state.search_performed = False
    else:
        st.session_state.search_performed = True
        st.session_state.location_name = location
        st.session_state.bbox = bbox_filter
        
        # Parse temporal filter
        temporal_filter = temporal_filter.split(", ")
        
        # Connect to the STAC API
        stac_url = "https://planetarycomputer.microsoft.com/api/stac/v1"
        client_st = Client.open(stac_url)

        # List all collections
        collections = client_st.get_collections()

        # Filter collections based on spatial and temporal criteria
        matching_collections = []
        for collection in collections:
            extent = collection.extent
            spatial_extent = extent.spatial.bboxes[0]
            temporal_extent = extent.temporal.intervals[0]

            if bbox_intersects(spatial_extent, bbox_filter) and temporal_intersects(temporal_extent, temporal_filter):
                matching_collections.append(collection)

        # Show the matching collections
        st.session_state.collection = matching_collections

        # Extract relevant information
        collection_info = []
        for collection in matching_collections:
            info = {
                "name": collection.id,
                "description": collection.description
            }
            collection_info.append(info)

        # Store collection info in session state
        st.session_state.collection_info = collection_info

        # # Generate summary
        # prompt = f"Summarize insights on how the following geospatial data could help with the ESG estimate of {location}:\n\n{matching_collections}"
        # st.session_state.report = generate_text(prompt)

        # Reset the visualization data when performing a new search
        st.session_state.selected_collection = None
        st.session_state.visualization_data = None
        st.session_state.item_info = None
        st.session_state.analysis_results = None

# Display results (outside the button click handler)
if st.session_state.search_performed:
    # Create a two-column layout for the main content
    col1, col2 = st.columns(2)
    
    # Display the search results in the first column
    with col1:
        # Show the area being searched without overlapping previous st.write results
        st.info(f"Searching in area: {st.session_state.location_name}")
        map = display_area_map(st.session_state.bbox)
        st_folium(map, width=None, height=400)
        
        # Show the collections and insights
        if st.session_state.collection:
            matching_collections = [collection for collection in st.session_state.collection]
            st.subheader(f"Available Data Collections: {len(matching_collections)}")
            # Create expandable section for the JSON data
            with st.expander("View Collection Details"):
                st.json(st.session_state.collection_info)

    with col2:      
        if st.session_state.report:
            st.subheader("ESG Insights:")
            st.write(st.session_state.report)
            
    # Add collection selection and data visualization below
    if st.session_state.collection_info:
        st.header("Data Visualization")
        
        # Create a dropdown to select a collection to visualize
        collection_names = [c["name"] for c in st.session_state.collection_info]
        collection_descriptions = {c["name"]: c["description"] for c in st.session_state.collection_info}
        
        selected_collection = st.selectbox(
            "Select a collection to visualize:", 
            collection_names,
            format_func=lambda x: f"{x} - {collection_descriptions[x][:50]}..."
        )
        
        # When a collection is selected, fetch and visualize the data
        if selected_collection and (st.session_state.selected_collection != selected_collection or st.button("Visualize Data")):
            st.session_state.selected_collection = selected_collection
            
            with st.spinner(f"Fetching and processing data from {selected_collection}..."):
                # Call the function to access and visualize data
                # Split the string on comma and remove any extra spaces
                st.write("Type:", type(temporal_filter))
                st.write("Content:", temporal_filter)
                start_date = temporal_filter[0]
                end_date = temporal_filter[1]
                date_range = f"{start_date}/{end_date}"
                st.write(date_range)

                dates = [date.strip() for date in temporal_filter.split(",")]
                # Now join with a "/"
                date_range = "/".join(dates)
                st.write(date_range)
                visualization, item_info, analysis = access_and_visualize_data(
                    selected_collection, 
                    st.session_state.bbox, 
                    date_range, 
                    st.session_state.location_name
                )
                st.write(visualization, item_info, analysis, date_range)
                
                # Store results in session state
                st.session_state.visualization_data = visualization
                st.session_state.item_info = item_info
                st.session_state.analysis_results = analysis
                
        # Display visualization and analysis results if available
        if st.session_state.visualization_data is not None:
            # Display visualization
            st.subheader(f"Visualization for {st.session_state.selected_collection}")
            
            # Handle different types of visualization data
            if isinstance(st.session_state.visualization_data, folium.Map):
                st.write("Raster Data Visualization:")
                st_folium(st.session_state.visualization_data, width=None, height=500)
            elif isinstance(st.session_state.visualization_data, gpd.GeoDataFrame):
                st.write("Vector Data Preview:")
                st.write(st.session_state.visualization_data.head())
            elif isinstance(st.session_state.visualization_data, pd.DataFrame):
                st.write("Tabular Data Preview:")
                st.write(st.session_state.visualization_data.head())
            
            # Show item metadata
            if st.session_state.item_info:
                with st.expander("Item Metadata"):
                    st.json(st.session_state.item_info)
            
            # Show analysis results
            if isinstance(st.session_state.analysis_results, dict):
                st.subheader("Data Analysis Results:")
                st.json(st.session_state.analysis_results)
                
                # Generate ESG-specific insights based on the analysis
                if st.button("Generate ESG Insights from Data"):
                    with st.spinner("Generating insights..."):
                        insights_prompt = f"""
                        Based on the following data analysis from {st.session_state.selected_collection} for {st.session_state.location_name}, 
                        provide detailed ESG insights:
                        
                        {st.session_state.analysis_results}
                        
                        Focus on environmental, social, and governance implications of this data. 
                        How can this information be used for ESG reporting and decision-making?
                        """
                        insights = generate_text(insights_prompt)
                        st.subheader("Data-Driven ESG Insights:")
                        st.write(insights)
            else:
                st.error(f"Error: {st.session_state.analysis_results}")
