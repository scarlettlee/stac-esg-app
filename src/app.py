# src/app.py

import streamlit as st
import os
from dotenv import load_dotenv
from components.sidebar import render_sidebar
from components.maps import display_area_map
from services.geocoding import get_bounding_box
from services.stac_service import search_stac_collections
from services.gemini_service import generate_esg_insights
from services.openai_service import generate_text
from services.geospatial_data_service import fetch_geospatial_data, load_and_display_data
from utils.extract_subsector_info import extract_subsector_info
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from rasterio.plot import show
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state
def init_session_state():
    """Initialize session state variables if they don't exist."""
    if 'search_performed' not in st.session_state:
        st.session_state.search_performed = False
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'location_name' not in st.session_state:
        st.session_state.location_name = None
    if 'bbox' not in st.session_state:
        st.session_state.bbox = None
    if 'collection' not in st.session_state:
        st.session_state.collection = None
    if 'collection_info' not in st.session_state:
        st.session_state.collection_info = None
    if 'report' not in st.session_state:
        st.session_state.report = None
    if 'sector' not in st.session_state:
        st.session_state.sector = None
    if 'subsector' not in st.session_state:
        st.session_state.subsector = None

def main():
    """Main application function."""
    try:
        # Initialize session state
        init_session_state()

        # Application title
        st.title("Inspect Geospatial Data for ESG")
        
        # Render sidebar and get inputs
        sidebar_inputs = render_sidebar()
        
        # Process search when button is clicked
        if sidebar_inputs["search_clicked"]:
            process_search(sidebar_inputs)
            
        # Display results if search has been performed
        if st.session_state.search_performed:
            display_results()
            
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("An error occurred. Please try again or contact support.")

def process_search(sidebar_inputs):
    """Process search based on sidebar inputs."""
    try:
        # Get location bounding box
        bbox_filter = get_bounding_box(sidebar_inputs["location"])
        
        if bbox_filter is None:
            st.error("Could not find the specified location. Please try a different location name.")
            st.session_state.search_performed = False
            return
            
        # Update session state
        st.session_state.search_performed = True
        st.session_state.location_name = sidebar_inputs["location"]
        st.session_state.bbox = bbox_filter
        st.session_state.sector = sidebar_inputs["sector"]
        st.session_state.subsector = sidebar_inputs["subsector"]
        
        # Search STAC collections
        with st.spinner("Searching for relevant data collections..."):
            # Use a default date range since time period filtering was removed
            date_range = "2020-01-01, 2025-12-31"
            
            matching_collections, collection_info = search_stac_collections(
                bbox_filter=bbox_filter,
                temporal_filter=date_range
            )
            
        st.session_state.collection = matching_collections
        st.session_state.collection_info = collection_info   
            
    except Exception as e:
        logger.error(f"Search processing error: {str(e)}")
        st.error("Error processing search. Please try again with different parameters.")

def display_topic_metrics(selected_topic, subsector_info):
    """Display metrics for a selected topic."""
    # Filter metrics for the selected topic
    metrics = subsector_info[subsector_info['Topic'] == selected_topic]['Accounting Metric']
    
    with st.expander("View Metrics", expanded=True):
        metrics_text = "\n".join([f"- {metric}" for metric in metrics])
        st.markdown(metrics_text)

def generate_search_prompt(location, sector, subsector, collections):
    """Generate prompt for OpenAI based on search context."""
    return f"""Analyze how the following geospatial data collections could help with ESG assessment for a {subsector} company in the {sector} sector located in {location}.

Focus on:
1. Environmental impact assessment
2. Social responsibility metrics
3. Governance implications
4. Specific ESG risks and opportunities
5. Data-driven insights and recommendations

Available data collections:
{[collection.id for collection in collections]}"""

def display_results():
    """Display search results and insights."""
    try:
        # Show search area
        st.info(f"📍 Analyzing area: {st.session_state.location_name}")
        subsector_info = extract_subsector_info('./src/data/SASB standard.xlsx', st.session_state.subsector)
        
        # add a second level title for the subsector
        st.subheader(f"Step 1: Company ESG Risk Profile")        
        # Display subsector information
        st.write("Below are the key material risks impacting your company's financial performance, identified through an environmental, social, and governance (ESG) lens.")

        # Display subsector information with side-by-side layout
        topics = subsector_info['Topic'].unique()
               
        # Create tabs with better spacing and visibility
        tab_labels = [topic.strip() for topic in topics]
        
        # Use a more robust tab system to ensure all tabs are visible
        if len(tab_labels) > 0:
            # Add custom CSS to improve tab display and ensure all tabs are visible
            st.markdown("""
            <style>
            .stTabs [data-baseweb="tab-list"] {
                gap: 12px;
                overflow-x: auto;
                flex-wrap: wrap;
                max-width: 100%;
                padding: 8px 0;
                border-bottom: 2px solid #e0e0e0;
                background: #f8f9fa;
                border-radius: 8px 8px 0 0;
            }
            .stTabs [data-baseweb="tab"] {
                height: auto;
                white-space: nowrap;
                min-width: fit-content;
                max-width: none;
                flex-shrink: 0;
                padding: 8px 16px;
                margin: 0 2px;
                border-radius: 6px 6px 0 0;
                border: 1px solid #d0d0d0;
                border-bottom: none;
                background: #ffffff;
                color: #666;
                font-weight: 500;
                transition: all 0.2s ease;
            }
            .stTabs [data-baseweb="tab"]:hover {
                background: #f0f0f0;
                color: #333;
                transform: translateY(-1px);
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                background: #ffffff;
                color: #1f77b4;
                border-color: #1f77b4;
                border-bottom: 2px solid #ffffff;
                font-weight: 600;
                box-shadow: 0 2px 8px rgba(31,119,180,0.15);
            }
            .stTabs [data-baseweb="tab-panel"] {
                padding: 1.5rem;
                background: #ffffff;
                border: 1px solid #d0d0d0;
                border-top: none;
                border-radius: 0 0 8px 8px;
                margin-top: -1px;
            }
            /* Ensure horizontal scrolling works properly */
            .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
                height: 8px;
            }
            .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-track {
                background: #f1f1f1;
                border-radius: 4px;
            }
            .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 4px;
            }
            .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
            /* Add visual separator between tabs */
            .stTabs [data-baseweb="tab"]:not(:last-child)::after {
                content: '';
                position: absolute;
                right: -6px;
                top: 50%;
                transform: translateY(-50%);
                width: 1px;
                height: 60%;
                background: #e0e0e0;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Try to use tabs, but if there are too many, use a selectbox approach
            if len(tab_labels) <= 6:  # Use tabs for 6 or fewer topics
                tabs = st.tabs(tab_labels)
                
                for i, tab in enumerate(tabs):
                    with tab:
                        selected_topic = topics[i]
                        display_topic_metrics(selected_topic, subsector_info)
            else:  # Use selectbox for many topics
                st.info("📋 Many ESG topics found. Use the dropdown below to explore each topic.")
                selected_topic = st.selectbox(
                    "Select ESG Topic to View:",
                    options=tab_labels,
                    index=0,
                    help="Choose a topic to view its associated metrics and risks"
                )
                display_topic_metrics(selected_topic, subsector_info)

        # Create two columns for map and dataset
        st.subheader("Step 2: Geospatial Data")
        # Create two columns for map and insights
        col1, col2 = st.columns([3, 2])
        
        with col1:            
            map = display_area_map(st.session_state.bbox)
            st_folium(map, width=None, height=600)
            
        with col2:
            # Display collection information
            if st.session_state.collection_info:
                # st.subheader("Available Data Collections")
                
                # Create tabs for different views
                tab1, tab2 = st.tabs(["Summary", "Detailed View"])
                
                with tab1:
                    # Display summary metrics
                    metrics_cols = st.columns(3)
                    with metrics_cols[0]:
                        st.metric("Total Collections", len(st.session_state.collection_info))
                    with metrics_cols[1]:
                        temporal_range = calculate_temporal_range()
                        st.metric("Time Range", temporal_range)
                    with metrics_cols[2]:
                        st.metric("Area Coverage", f"{calculate_area_coverage():.2f} km²")
                        
                with tab2:
                    # Display detailed collection information
                    for idx, collection in enumerate(st.session_state.collection_info):
                        with st.expander(f"{collection['title']} ({collection['id']})"):
                            st.markdown(f"**Description:** {collection['description']}")
                            st.markdown(f"**License:** {collection['license']}")
                            if collection['keywords']:
                                st.markdown(f"**Keywords:** {', '.join(collection['keywords'])}")

        st.subheader("Step 3: ESG Insights")
        # Generate insights
        if st.session_state.collection:
            with st.spinner("Generating ESG insights..."):
                prompt = generate_search_prompt(
                    location=st.session_state.location_name,
                    sector=st.session_state.sector,
                    subsector=st.session_state.subsector,
                    collections=st.session_state.collection
                )
                st.session_state.report = generate_text(prompt)
        else:
            st.warning("No matching data collections found for the specified criteria.")

        if st.session_state.report:
            st.markdown(st.session_state.report)        

        # # Add a section for data visualization and statistics
        # st.subheader("Step 4: Data Visualization and Analysis")
        
        # # Let user select a collection to explore
        # if st.session_state.collection:
        #     collection_ids = [c.id for c in st.session_state.collection]   
        #     # Check if 'landsat-c2-l2' is in the list to set it as default
        #     if 'landsat-c2-l2' in collection_ids:
        #         default_index = collection_ids.index('landsat-c2-l2')
        #     else:
        #         default_index = 0  # Use the first item as default if not found

        #     # Create a selectbox with a default selection
        #     selected_collection = st.selectbox(
        #         "Select a data collection to visualize:",
        #         collection_ids,
        #         index=default_index
        #     )      
            
        #     # Determine data type (raster or vector)
        #     data_type = "raster"  # Default, you could add logic to determine this from collection metadata
            
        #     # Fetch the data
        #     with st.spinner("Fetching geospatial data..."):
        #         try:
        #             item, url_or_message = fetch_geospatial_data(
        #                 selected_collection, 
        #                 st.session_state.bbox,
        #                 "2024-08-27/2024-08-28"  # Example time range, you may want to use user input
        #             )
        #             # st.write(f"Data source: {item},{url_or_message}")
                    
        #             if item:
        #                 # Create columns for visualization and statistics
        #                 viz_col, stats_col = st.columns([3, 1])
                        
        #                 with viz_col:
        #                     st.subheader("Data Visualization")
                            
        #                     # Load and process the data
        #                     data, metadata, stats = load_and_display_data(item, url_or_message, data_type)
                            
        #                     # if data is not None:
        #                     #     # Display the data
        #                     #     if data_type == "raster":
        #                     #         # Normalize for display if needed
        #                     #         fig, ax = plt.subplots(figsize=(10, 10))
        #                     #         show(data, ax=ax)
        #                     #         st.pyplot(fig)
        #                     #     else:  # Vector
        #                     #         st.write("Vector data loaded:")
        #                     #         st.write(data.head())
        #                     #         # Plot the vector data
        #                     #         fig, ax = plt.subplots(figsize=(10, 10))
        #                     #         data.plot(ax=ax)
        #                     #         st.pyplot(fig)
        #                     # else:
        #                     #     st.error(f"Failed to load data: {stats}")
                        
        #                 with stats_col:
        #                     st.subheader("Statistics")
        #                     if isinstance(stats, dict):
        #                         st.write("Basic Statistics:")
        #                         st.json(stats)
        #                     else:
        #                         st.error(stats)
        #             else:
        #                 st.error(f"Could not fetch data: {url_or_message}")
        #         except Exception as e:
        #             st.error("An error occurred while fetching geospatial data. Please try again: {str(e)}")
        # else:
        #     st.warning("No collections available to visualize.")

    except Exception as e:
        st.error("Error displaying results. Please try refreshing the page: {str(e)}")

def calculate_temporal_range():
    """Calculate the temporal range of available data."""
    if not st.session_state.collection:
        return "N/A"
    # Implementation details...
    return "Temporal range calculation"

def calculate_area_coverage():
    """Calculate the approximate area coverage in square kilometers."""
    if not st.session_state.bbox:
        return 0
    # Implementation details...
    return 1000  # Placeholder

if __name__ == "__main__":
    # Page configuration
    st.set_page_config(
        page_title="ESG Geospatial Data Inspector",
        page_icon="🌍",
        layout="wide"
    )
    main()
