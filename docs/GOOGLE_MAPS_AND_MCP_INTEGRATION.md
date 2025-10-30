# Google Maps and MCP Integration Guide

This document explains how to use Google Maps (instead of Folium) and MCP (Model Context Protocol) in the ESG Geospatial Data Inspector application.

## Table of Contents

1. [Overview](#overview)
2. [Google Maps Integration](#google-maps-integration)
3. [MCP Integration](#mcp-integration)
4. [Setup Instructions](#setup-instructions)
5. [Usage Examples](#usage-examples)
6. [Architecture](#architecture)
7. [Future Enhancements](#future-enhancements)

---

## Overview

This integration adds two major capabilities to your ESG application:

1. **Google Maps**: Replace Folium maps with Google Maps for better interactivity and satellite imagery
2. **MCP (Model Context Protocol)**: Enable AI agents to access STAC API and other tools through a standardized protocol

### Key Benefits

- **Google Maps**: Enhanced satellite imagery, better interactivity, professional appearance
- **MCP**: Standardized way to expose tools to AI models (Gemini, GPT, etc.)
- **Extensible**: Easy to add new tools and data sources
- **Future-proof**: Foundation for advanced AI workflows

---

## Google Maps Integration

### Features

- **Satellite Imagery**: High-resolution satellite imagery from Google
- **Interactive Maps**: Zoom, pan, and explore the area
- **Bounding Box Visualization**: Red rectangle shows the search area
- **Seamless Integration**: Toggle between Folium and Google Maps in the sidebar

### How to Use

1. **Get a Google Maps API Key**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable "Maps JavaScript API"
   - Create an API key
   - (Optional) Restrict the API key to your domain

2. **Configure Environment**
   ```bash
   # Add to your .env file:
   GOOGLE_MAPS_API_KEY=your_actual_api_key_here
   ```

3. **Use in the App**
   - Open the application
   - Check the "Use Google Maps" checkbox in the sidebar
   - Run a search to see the Google Maps rendering

### Code Structure

```
src/components/
├── google_maps.py          # Google Maps integration functions
├── maps.py                 # Updated to support both Folium and Google Maps
└── sidebar.py              # Added toggle for map selection
```

### Key Functions

#### `display_google_map()`
Main function to display Google Maps in Streamlit:
```python
from components.google_maps import display_google_map

display_google_map(
    bbox=[-74.05, 40.70, -73.93, 40.80],  # NYC
    zoom_level=10,
    map_type="satellite",
    show_marker=True,
    location_name="New York City"
)
```

#### `create_google_map_html()`
Creates the HTML/JavaScript for Google Maps embedding:
```python
html = create_google_map_html(
    bbox=bbox,
    api_key=api_key,
    zoom_level=10,
    map_type="satellite"
)
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `bbox` | List[float] | Required | Bounding box coordinates |
| `zoom_level` | int | 0 | Zoom level (0 = auto-calculate) |
| `map_type` | str | "satellite" | Map type: satellite, roadmap, hybrid, terrain |
| `show_marker` | bool | True | Show center marker |
| `location_name` | str | None | Location label for marker |
| `height` | int | 600 | Map height in pixels |

---

## MCP Integration

### What is MCP?

**Model Context Protocol (MCP)** is a standardized protocol that allows AI models to:
- Access external tools and APIs
- Retrieve data from databases and services
- Interact with local resources
- Chain multiple operations together

### Why Use MCP?

1. **Standardized Interface**: Same pattern for all AI tools
2. **Extensibility**: Easy to add new tools
3. **Flexibility**: Works with any MCP-compatible AI model
4. **Safety**: Controlled access to resources
5. **Reusability**: Tools can be used across different AI agents

### MCP Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Service                          │
│                                                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐      │
│  │ STAC Tool  │  │Geocoding   │  │ ESG Topics │      │
│  │            │  │  Tool      │  │   Tool     │      │
│  └────────────┘  └────────────┘  └────────────┘      │
│                                                         │
└─────────────────┬───────────────────┬───────────────────┘
                  │                   │
                  ▼                   ▼
          ┌──────────────┐    ┌──────────────┐
          │  STAC API    │    │ AI Agents    │
          │  (external)  │    │ (Gemini/     │
          │              │    │  GPT/Claude) │
          └──────────────┘    └──────────────┘
```

### Available MCP Tools

#### 1. `search_stac_collections`
Search Microsoft Planetary Computer for geospatial datasets.

**Parameters:**
- `bbox`: [min_lon, min_lat, max_lon, max_lat] - Bounding box
- `datetime`: ISO 8601 datetime range (optional)
- `collections`: List of collection IDs (optional)

**Example:**
```python
result = mcp_service.call_tool(
    "search_stac_collections",
    {
        "bbox": [-74.05, 40.70, -73.93, 40.80],
        "datetime": "2023-01-01, 2024-12-31"
    }
)
# Returns: {"collections": [...], "count": 5}
```

#### 2. `geocode_location`
Convert location name to coordinates.

**Parameters:**
- `location`: Location name or address

**Example:**
```python
result = mcp_service.call_tool(
    "geocode_location",
    {"location": "Tokyo, Japan"}
)
# Returns: {"coordinates": {...}, "bounding_box": [...]}
```

#### 3. `get_esg_topics`
Get ESG disclosure topics for a subsector.

**Parameters:**
- `subsector`: Industry subsector name

**Example:**
```python
result = mcp_service.call_tool(
    "get_esg_topics",
    {"subsector": "Software & IT Services"}
)
# Returns: {"topics": [...], "count": 10}
```

### Extending MCP Tools

Add your own tool:

```python
from services.mcp_service import get_mcp_service

# Create a custom handler function
def handle_my_custom_tool(param1: str, param2: int):
    # Your logic here
    return {"result": "data"}

# Register the tool
mcp_service = get_mcp_service()
mcp_service.register_tool(
    name="my_custom_tool",
    description="Does something useful",
    parameters={
        "type": "object",
        "properties": {
            "param1": {"type": "string"},
            "param2": {"type": "integer"}
        },
        "required": ["param1"]
    },
    handler=handle_my_custom_tool,
    enabled=True
)
```

---

## Setup Instructions

### Prerequisites

1. Python 3.9+
2. Required API keys:
   - Google Maps API Key
   - (Optional) AI API keys for future AI integration

### Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   
   Create a `.env` file in the project root:
   ```bash
   # Copy the template
   cp env_template.txt .env
   
   # Edit .env and add your keys
   GOOGLE_MAPS_API_KEY=your_actual_key
   GOOGLE_API_KEY=your_gemini_key
   OPENAI_API_KEY=your_openai_key
   ```

3. **Get API Keys**
   
   **Google Maps API Key:**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create project → Enable "Maps JavaScript API"
   - Create credentials → API key
   - (Recommended) Restrict to HTTP referrers
   
   **AI API Keys:**
   - OpenAI: https://platform.openai.com/
   - Google Gemini: https://makersuite.google.com/app/apikey

### Run the Application

```bash
streamlit run src/app.py
```

### Test the Integration

1. **Test Google Maps**
   - Open the app
   - Check "Use Google Maps" in sidebar
   - Run a search
   - Verify satellite imagery appears

2. **Test MCP Service**
   ```bash
   cd src/examples
   python mcp_stac_demo.py
   ```

---

## Usage Examples

### Example 1: Using Google Maps in Streamlit

```python
import streamlit as st
from components.google_maps import display_google_map

# In your Streamlit app
bbox = [-74.05, 40.70, -73.93, 40.80]  # NYC
display_google_map(
    bbox=bbox,
    map_type="satellite",
    location_name="New York City"
)
```

### Example 2: Using MCP Tools Programmatically

```python
from services.mcp_service import get_mcp_service

mcp_service = get_mcp_service()

# Search for STAC collections
result = mcp_service.call_tool(
    "search_stac_collections",
    {
        "bbox": [-122.5, 37.7, -122.3, 37.9],  # San Francisco
        "datetime": "2023-01-01, 2024-12-31"
    }
)

print(f"Found {result['count']} collections")
```

### Example 3: Custom MCP Tool for ESG Analysis

```python
from services.mcp_service import get_mcp_service

def analyze_esg_risk(location: str, sector: str):
    """Custom tool to analyze ESG risks for a location."""
    # Your analysis logic here
    return {
        "location": location,
        "sector": sector,
        "risk_level": "moderate",
        "key_risks": ["Climate", "Water scarcity"]
    }

# Register the tool
mcp_service = get_mcp_service()
mcp_service.register_tool(
    "analyze_esg_risk",
    "Analyze ESG risks for a location and sector",
    {
        "type": "object",
        "properties": {
            "location": {"type": "string"},
            "sector": {"type": "string"}
        },
        "required": ["location", "sector"]
    },
    analyze_esg_risk
)

# Use the tool
result = mcp_service.call_tool(
    "analyze_esg_risk",
    {"location": "New York", "sector": "Technology"}
)
```

### Example 4: AI Agent Workflow (Future)

```python
# This is how you would use MCP with an AI agent:

# 1. Initialize AI agent with MCP support
agent = GeminiAgent(
    api_key=os.getenv('GOOGLE_API_KEY'),
    tools=get_mcp_service().list_tools()
)

# 2. User query
response = agent.chat(
    "Find satellite imagery of deforestation in the Amazon"
)

# 3. AI agent automatically:
#    - Calls geocode_location("Amazon rainforest")
#    - Calls search_stac_collections with bbox
#    - Returns relevant imagery
```

---

## Architecture

### Google Maps Flow

```
User Input → Sidebar Toggle → Google Maps Component
                                        ↓
                              Google Maps JavaScript API
                                        ↓
                           Embed HTML in Streamlit via components.html()
```

### MCP Service Flow

```
AI Agent Request → MCP Service → Tool Handler → External API/Service
                                                      ↓
                                            Return Results → AI Agent
```

### Integration Points

1. **MCP ↔ STAC API**: Direct integration for geospatial data
2. **MCP ↔ Geocoding**: Nominatim/Google Maps integration
3. **MCP ↔ ESG Data**: SASB standards database
4. **MCP ↔ AI Agents**: Tool exposure for AI models

---

## Future Enhancements

### Phase 1: Immediate (Current)
- ✅ Google Maps integration
- ✅ MCP service framework
- ✅ Basic tools (STAC, Geocoding, ESG)

### Phase 2: Near-term
- [ ] Integrate MCP with AI agents (Gemini, GPT)
- [ ] Add more STAC-specific tools
- [ ] Implement MCP server for external access
- [ ] Add authentication and security

### Phase 3: Advanced
- [ ] Real-time data streaming via MCP
- [ ] Multi-agent workflows
- [ ] Tool chaining and composition
- [ ] Custom AI model training with MCP

### Suggested Custom Tools

1. **`get_environmental_indicators`**: Fetch environmental data for a location
2. **`compare_locations`**: Compare ESG metrics across multiple locations
3. **`predict_esg_risk`**: ML-based ESG risk prediction
4. **`get_historical_trends`**: Analyze temporal trends in data
5. **`generate_esg_report`**: Automated report generation

---

## Troubleshooting

### Google Maps Issues

**Problem**: Map not displaying
- **Solution**: Check `GOOGLE_MAPS_API_KEY` in `.env`
- **Solution**: Verify API key has correct permissions
- **Solution**: Check browser console for JavaScript errors

**Problem**: API key errors
- **Solution**: Enable "Maps JavaScript API" in Google Cloud Console
- **Solution**: Check API key restrictions

### MCP Service Issues

**Problem**: Tool not found
- **Solution**: Ensure tool is registered via `register_tool()`
- **Solution**: Check `enabled=True`

**Problem**: Import errors
- **Solution**: Ensure `mcp` package is installed: `pip install mcp`
- **Solution**: Check Python path and imports

---

## Additional Resources

- [Google Maps JavaScript API](https://developers.google.com/maps/documentation/javascript)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Streamlit Components](https://docs.streamlit.io/library/components/create-a-component)
- [STAC API Specification](https://stacspec.org/)

---

## Summary

This integration provides:

1. **Enhanced Mapping**: Professional Google Maps with satellite imagery
2. **AI-Ready**: MCP foundation for AI agent integration
3. **Extensible**: Easy to add new tools and capabilities
4. **Production-Ready**: Error handling, configuration, documentation

The combination of Google Maps + MCP creates a powerful foundation for building advanced AI-driven ESG analysis tools.

**Happy coding! 🚀**

