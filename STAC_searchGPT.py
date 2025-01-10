import streamlit as st
import openai
from pystac_client import Client
from geopy.geocoders import Nominatim
import pycountry
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a geospatial data expert and good at ESG research."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content'].strip()

# Function to get bounding box for a location
def get_bounding_box(location):
    geolocator = Nominatim(user_agent="stac_search_app")
    loc = geolocator.geocode(location)
    if loc:
        return [loc.longitude - 0.1, loc.latitude - 0.1, loc.longitude + 0.1, loc.latitude + 0.1]
    else:
        return None
    
# Streamlit UI
st.title("Inspect Geospatial Data for ESG")
st.sidebar.header("Filters")
bbox_filter = st.sidebar.text_input("Bounding Box (comma-separated)", "-135.17, 36.83, -51.24, 62.25")
temporal_filter = st.sidebar.text_input("Date Range (comma-separated)", "2020-01-01, 2023-01-01")

if st.sidebar.button("Search and Generate Data insights"):
    # Parse filters
    bbox_filter = [float(x) for x in bbox_filter.split(", ")]
    temporal_filter = temporal_filter.split(", ")    

    # Connect to the STAC API
    stac_url = "https://planetarycomputer.microsoft.com/api/stac/v1"
    client = Client.open(stac_url)

    # List all collections
    collections = client.get_collections()

    # Filter collections based on spatial and temporal criteria
    matching_collections = []
    for collection in collections:
        extent = collection.extent
        spatial_extent = extent.spatial.bboxes[0]  # Get the spatial bounding box
        temporal_extent = extent.temporal.intervals[0]  # Get the temporal interval

        # Check for intersection
        if bbox_intersects(spatial_extent, bbox_filter) and temporal_intersects(temporal_extent, temporal_filter):
            matching_collections.append(collection)

    # Extract relevant information from matching collections
    collection_info = []
    for collection in matching_collections[0:5]:
        info = {
            "name": collection.id,
            "description": collection.description
        }
        collection_info.append(info)

    # Generate summary using OpenAI GPT
    prompt = f"Generate insights on how the following geospatialdata could help with the ESG estimate of the target region:\n\n{collection_info}"

    report = generate_text(prompt)

    # Display the insights
    # st.header("Inspect Geospatial Data for ESG")
    st.write(report)