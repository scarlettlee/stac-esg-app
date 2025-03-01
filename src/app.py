# src/app.py

import streamlit as st
from components.sidebar import render_sidebar
from components.maps import display_area_map
from services.geocoding import get_bounding_box
from services.stac_service import search_stac_collections
from services.openai_service import generate_text
from utils.extract_subsector_info import extract_subsector_info
from streamlit_folium import st_folium
import logging

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
    if 'subsector' not in st.session_state:
        st.session_state.subsector = None

def main():
    """Main application function."""
    try:
        # Initialize session state
        init_session_state()

        # Application title
        st.title("Inspect Geospatial Data for ESG-")
        
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
        st.session_state.subsector = sidebar_inputs["subsector"]
        
        # Search STAC collections
        with st.spinner("Searching for relevant data collections..."):
            # Ensure temporal_filter is a string before splitting
            date_range = sidebar_inputs["date_range"]
            if isinstance(date_range, list):
                date_range = ", ".join(date_range)
            
            matching_collections, collection_info = search_stac_collections(
                bbox_filter=bbox_filter,
                temporal_filter=date_range
            )
            
        st.session_state.collection = matching_collections
        st.session_state.collection_info = collection_info
        
        # # Generate insights
        # if matching_collections:
        #     with st.spinner("Generating ESG insights..."):
        #         prompt = generate_search_prompt(
        #             location=sidebar_inputs["location"],
        #             sector=sidebar_inputs["sector"],
        #             subsector=sidebar_inputs["subsector"],
        #             collections=matching_collections
        #         )
        #         st.session_state.report = generate_text(prompt)
        # else:
        #     st.warning("No matching data collections found for the specified criteria.")
            
    except Exception as e:
        logger.error(f"Search processing error: {str(e)}")
        st.error("Error processing search. Please try again with different parameters.")

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
        
        # Display subsector information with side-by-side layout
        topics = subsector_info['Topic'].unique()
               
        # Create two columns for topics and metrics
        # Ensure tab labels are properly formatted
        tab_labels = [topic.strip() for topic in topics]
        tabs = st.tabs(tab_labels)
        
        for i, tab in enumerate(tabs):
            with tab:
                selected_topic = topics[i]

                # Filter metrics for the selected topic
                metrics = subsector_info[subsector_info['Topic'] == selected_topic]['Accounting Metric']
                
                with st.expander("View Metrics", expanded=True):
                    metrics_text = "\n".join([f"- {metric}" for metric in metrics])
                    st.markdown(metrics_text)

        # Create two columns for map and insights
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("Geographic Area")
            map = display_area_map(st.session_state.bbox)
            st_folium(map, width=None, height=600)
            
        with col2:
            if st.session_state.report:
                st.subheader("ESG Insights")
                st.markdown(st.session_state.report)
                
        # Display collection information
        if st.session_state.collection_info:
            st.subheader("Available Data Collections")
            
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
                        
    except Exception as e:
        logger.error(f"Display error: {str(e)}")
        st.error("Error displaying results. Please try refreshing the page.")

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
