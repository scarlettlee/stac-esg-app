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

# Load environment variables
load_dotenv()
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Add this near the top of the file after imports
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False
    st.session_state.search_results = None
    st.session_state.location_name = None
    st.session_state.bbox = None
    st.session_state.collection = None
    st.session_state.collection_info = None
    st.session_state.report = None

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

# Streamlit UI
st.title("Inspect Geospatial Data for ESG")
st.sidebar.header("Filters")

# Replace the bbox_filter input with address input
location = st.sidebar.text_input("Location (e.g., 'New York City' or 'Tokyo, Japan')", "New York City")
temporal_filter = st.sidebar.text_input("Date Range (comma-separated)", "2020-01-01, 2025-12-31")

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

        # Generate summary
        prompt = f"Summarize insights on how the following geospatial data could help with the ESG estimate of {location}:\n\n{matching_collections}"
        st.session_state.report = generate_text(prompt)

# Display results (outside the button click handler)
if st.session_state.search_performed:
    # Show the area being searched without overlapping previous st.write results
    st.info(f"Searching in area: {st.session_state.location_name}")
    map = display_area_map(st.session_state.bbox)
    st_folium(map, width=700)

    # Show the collections and insights
    if st.session_state.collection:
        matching_collections = [collection for collection in st.session_state.collection]
        st.subheader(f"Available Data Collections: {len(matching_collections)}")
        st.json(st.session_state.collection)
    
    # # Display collections and insights
    # if st.session_state.collection_info:
    #     st.subheader("Available Data Collections")
    #     st.json(st.session_state.collection_info)
    
    if st.session_state.report:
        st.subheader("ESG Insights:")
        st.write(st.session_state.report)