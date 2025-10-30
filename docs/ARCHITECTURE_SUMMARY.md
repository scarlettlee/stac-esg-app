# ESG Geospatial Data Inspector - Architecture Summary

## 📋 Project Overview

**Purpose**: A Streamlit-based web application that combines ESG (Environmental, Social, Governance) analysis with geospatial data exploration to help companies assess ESG risks using satellite imagery and spatial data.

**Core Value**: Enables data-driven ESG assessment by combining industry-standard frameworks (SASB), professional geospatial sources (Microsoft Planetary Computer), and AI-powered insights.

---

## 🏗️ Architecture Overview

### Layered Architecture

```
┌─────────────────────────────────────────────────┐
│              Presentation Layer                 │
│  Streamlit UI Components (sidebar, maps)        │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│              Application Layer                   │
│  app.py - Main orchestrator                     │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│              Service Layer                       │
│  STAC, Geocoding, OpenAI, Gemini Services       │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│              Data Layer                          │
│  SASB Standards, Geographic Data, STAC API      │
└─────────────────────────────────────────────────┘
```

### Directory Structure

```
streamlit/
├── src/
│   ├── app.py                    # Main application entry point
│   ├── components/               # UI Components
│   │   ├── sidebar.py           # User input interface
│   │   └── maps.py              # Interactive mapping
│   ├── services/                # Business Logic
│   │   ├── stac_service.py      # STAC API integration
│   │   ├── geocoding.py         # Location services
│   │   ├── openai_service.py    # AI insights (OpenAI)
│   │   ├── gemini_service.py    # AI insights (Google Gemini)
│   │   └── geospatial_data_service.py  # Data processing
│   ├── config/                  # Configuration
│   │   └── sasb_sectors.py      # Industry definitions
│   ├── utils/                   # Utilities
│   │   ├── extract_subsector_info.py  # SASB parsing
│   │   ├── spatial_utils.py     # Spatial calculations
│   │   └── date_utils.py        # Date handling
│   └── data/                    # Static Data
│       ├── SASB standard.xlsx   # ESG standards
│       ├── us_cities.csv        # Geographic data
│       └── us_regions.geojson   # Regional boundaries
├── Dockerfile                   # Container config
├── requirements.txt             # Dependencies
└── cloudbuild.yaml             # CI/CD config
```

---

## 🔄 Logical Flow

### 1. **User Input** (src/components/sidebar.py)
- **Location**: Free-text input (e.g., "New York City")
- **Sector**: Select from 10 SASB sectors (e.g., "Technology & Communications")
- **Subsector**: Select from 77 subsectors (e.g., "Software & IT Services")

### 2. **Geocoding** (src/services/geocoding.py)
```python
get_bounding_box(location) → [min_lon, min_lat, max_lon, max_lat]
```
- Uses Nominatim (OpenStreetMap)
- Returns bounding box with 0.5° buffer
- Validates location existence

### 3. **STAC Collection Search** (src/services/stac_service.py)
```python
search_stac_collections(bbox_filter, temporal_filter)
```
- **Spatial Intersection**: Checks if collection bbox intersects user bbox
- **Temporal Intersection**: Validates date range overlap
- **Returns**: Matching collections + metadata

**Key Functions**:
- `bbox_intersects()` - Spatial overlap check
- `temporal_intersects()` - Date range validation
- `get_collection_info()` - Extract metadata

### 4. **ESG Risk Profile** (src/utils/extract_subsector_info.py)
- Loads SASB standards from Excel
- Extracts material disclosure topics
- Displays metrics by topic in tabs

### 5. **AI-Powered Insights** (src/services/openai_service.py or gemini_service.py)
```python
generate_text(prompt, sector, subsector)
```
- Constructs contextual prompt
- Calls OpenAI GPT-3.5-turbo OR Google Gemini 1.5 Flash
- Returns ESG insights and recommendations

### 6. **Visualization** (src/components/maps.py)
- Interactive Folium map with bounding box
- US cities and regional overlays
- Displays search area graphically

---

## 🔧 Key Components

### **app.py** - Application Orchestrator
**Responsibility**: Coordinates the entire application flow

**Session State Management**:
```python
- search_performed: bool
- location_name: str
- bbox: List[float]
- collection: List[Collection]
- sector/subsector: str
- report: str  # AI-generated insights
```

**Main Functions**:
1. `main()` - Entry point, error handling
2. `process_search()` - Coordinates search workflow
3. `display_results()` - Renders results in 3 steps:
   - Step 1: ESG Risk Profile (SASB topics)
   - Step 2: Geospatial Data (map + collections)
   - Step 3: ESG Insights (AI-generated)

### **sidebar.py** - User Input
**Widgets**:
- `render_sector_selection()` - Sector/subsector dropdowns
- `render_location_input()` - Location text input
- `render_sidebar()` - Complete sidebar assembly

**Returns**: Dict with sector, subsector, location, search_clicked

### **stac_service.py** - Geospatial Data Discovery
**Purpose**: Query Microsoft Planetary Computer for relevant datasets

**Workflow**:
1. Initialize STAC client
2. Get all available collections
3. Filter by spatial intersection (`bbox_intersects`)
4. Filter by temporal intersection (`temporal_intersects`)
5. Return matching collections

**Key Functions**:
- `initialize_stac_client()` - Connect to STAC API
- `search_stac_collections()` - Main search logic
- `get_collection_info()` - Extract metadata

### **geocoding.py** - Location Services
**Purpose**: Convert location names to geographic coordinates

**Implementation**:
- Uses Nominatim (OpenStreetMap)
- Returns bounding box [min_lon, min_lat, max_lon, max_lat]
- Applies 0.5° buffer around point location

### **AI Services** (openai_service.py / gemini_service.py)
**Purpose**: Generate ESG insights from available data

**Strategy**:
- Builds contextual prompt with sector/subsector info
- Includes available STAC collections
- Asks AI to provide ESG assessment and recommendations

**OpenAI**: GPT-3.5-turbo via chat completion API
**Gemini**: Gemini 1.5 Flash (alternative)

### **SASB Integration** (extract_subsector_info.py)
**Purpose**: Load industry-specific ESG disclosure standards

**Process**:
1. Load "SASB standard.xlsx"
2. Filter by sector/subsector
3. Extract topics and accounting metrics
4. Display in tabbed interface

---

## 🔗 External Dependencies

### APIs & Services
- **Microsoft Planetary Computer**: STAC API for satellite imagery
- **Nominatim (OpenStreetMap)**: Geocoding service
- **OpenAI API**: GPT-3.5-turbo for ESG insights
- **Google Gemini API**: Alternative AI service

### Key Libraries
- **Streamlit**: Web framework
- **Folium**: Interactive mapping
- **pystac-client**: STAC API client
- **geopy**: Geocoding
- **openai**: OpenAI API client
- **google-generativeai**: Gemini API client
- **pandas**: Data manipulation (SASB standards)
- **openpyxl**: Excel file reading

---

## 🚀 Data Flow Diagram

```
┌─────────────┐
│   User      │
│  Input      │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Sidebar        │
│  Component      │
└──────┬──────────┘
       │ Location, Sector, Subsector
       ▼
┌─────────────────┐      ┌──────────────────┐
│  Geocoding      │─────▶│  Bounding Box    │
│  Service        │      │  [lon, lat, ...] │
└──────┬──────────┘      └────────┬─────────┘
       │                          │
       │                          ▼
       │                 ┌─────────────────┐
       │                 │  STAC Service   │
       │                 │  Search         │
       │                 └────────┬────────┘
       │                          │
       │                          ▼
       │                 ┌─────────────────┐
       │                 │  Collections    │
       │                 │  + Metadata     │
       │                 └────────┬────────┘
       │                          │
       │                          ▼
       │                 ┌─────────────────┐
       ├────────────────▶│  ESG Topics     │
       │                 │  (SASB)          │
       │                 └────────┬────────┘
       │                          │
       │                          ▼
       │                 ┌─────────────────┐
       │                 │  AI Service     │
       │                 │  (OpenAI/Gemini)│
       │                 └────────┬────────┘
       │                          │
       ▼                          ▼
┌─────────────────────────────────────────┐
│         Display Results                 │
│  1. ESG Risk Profile (tabs)             │
│  2. Geospatial Data (map + info)       │
│  3. ESG Insights (AI-generated)         │
└─────────────────────────────────────────┘
```

---

## 🎯 Key Design Patterns

### 1. **Separation of Concerns**
- **Components**: UI rendering only
- **Services**: Business logic, API calls
- **Utils**: Reusable functions
- **Config**: Static data

### 2. **Session State Pattern**
Streamlit's session state maintains application state across reruns:
```python
st.session_state.search_performed = True
st.session_state.location_name = location
st.session_state.bbox = bbox_filter
```

### 3. **Lazy Initialization**
AI clients initialized only when needed:
```python
_client = None  # OpenAI client
def get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=api_key)
    return _client
```

### 4. **Error Handling**
Try-catch blocks with user-friendly messages:
```python
try:
    # Operation
except Exception as e:
    st.error(f"Error: {str(e)}")
    logger.error(f"Detailed: {str(e)}")
```

---

## 🔧 Extensibility Points

### **Adding New AI Providers**
Create `src/services/new_ai_service.py`:
```python
def generate_text(prompt: str, sector: str = None, subsector: str = None):
    # Implementation
    pass
```
Import in `app.py` and use in `generate_search_prompt()`.

### **Adding New Data Sources**
Extend `stac_service.py` to query additional STAC catalogs:
```python
# Add new client
new_client = Client.open("https://new-stac-catalog.com/api")
# Combine results from multiple sources
```

### **Adding New Visualizations**
Create components in `src/components/`:
```python
def render_chart(data):
    # Visualization logic
    pass
```
Call from `app.py` in `display_results()`.

### **Adding New ESG Frameworks**
Extend `src/config/` with new standards:
```python
NEW_FRAMEWORK = {
    "topic": ["metric1", "metric2"]
}
```
Load in `extract_subsector_info.py`.

---

## 🧪 Testing Strategy

### Unit Tests
- `spatial_utils.py` - Test bbox intersection logic
- `date_utils.py` - Validate date parsing
- `geocoding.py` - Mock geocoding responses

### Integration Tests
- STAC service with test collections
- AI services with mock responses
- End-to-end workflow

### Mock Services
```python
# Mock STAC client
class MockClient:
    def get_collections(self):
        return [mock_collection1, mock_collection2]
```

---

## 📊 State Management

### Session State Variables
```python
search_performed: bool        # Has search been run?
location_name: str            # User's location
bbox: List[float]             # Bounding box coordinates
collection: List              # Matching STAC collections
collection_info: List[Dict]   # Collection metadata
report: str                   # AI-generated insights
sector: str                   # Selected sector
subsector: str                # Selected subsector
```

### State Flow
1. **Initial State**: All variables = None/False
2. **Search Triggered**: User clicks "Search"
3. **Processing**: Update state with search results
4. **Display**: Use state to render results
5. **Reset**: New search clears and updates state

---

## 🚀 Deployment Architecture

### Production Stack
```
┌──────────────────┐
│   User Browser   │
└────────┬─────────┘
         │ HTTPS
         ▼
┌──────────────────┐
│  Google Cloud    │
│     Run          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Docker Container│
│  Streamlit App   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ External APIs    │
│ - STAC API       │
│ - OpenAI/Gemini  │
│ - Nominatim      │
└──────────────────┘
```

### CI/CD Pipeline (cloudbuild.yaml)
1. Build Docker image
2. Push to GCP Container Registry
3. Deploy to Cloud Run
4. Health check

---

## 🎯 Business Logic Summary

### ESG Assessment Workflow
1. **Industry Selection**: User selects sector → subsector
2. **Location Input**: Free-text location name
3. **Geocoding**: Location → Bounding box
4. **STAC Search**: Find intersecting datasets
5. **SASB Mapping**: Load relevant ESG topics
6. **AI Analysis**: Generate insights from data + context
7. **Visualization**: Map, data info, insights

### Key Algorithms
- **Spatial Intersection**: Check if two bounding boxes overlap
- **Temporal Intersection**: Validate date range overlap
- **Context Building**: Combine location + sector + collections → AI prompt

---

## 🔄 Session Lifecycle

```
┌─────────────────────────────────────────┐
│ Application Start                       │
│ - Load .env variables                   │
│ - Initialize session state              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ User Interface                          │
│ - Render sidebar with defaults          │
│ - Location: "New York City"             │
│ - Sector: "Technology & Communications" │
│ - Subsector: "Software & IT Services"   │
└──────────────┬──────────────────────────┘
               │ User clicks "Search"
               ▼
┌─────────────────────────────────────────┐
│ Processing Stage                        │
│ - Geocode location                      │
│ - Search STAC collections                │
│ - Extract ESG topics                    │
│ - Generate AI insights                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Results Display                         │
│ Step 1: ESG Risk Profile (tabs)         │
│ Step 2: Geospatial Data (map + info)    │
│ Step 3: ESG Insights (text)             │
└─────────────────────────────────────────┘
```

---

## 💡 Development Guidelines

### Adding Features

#### 1. **New UI Component**
- Create file in `src/components/`
- Import in `app.py`
- Call from appropriate function

#### 2. **New Service**
- Create file in `src/services/`
- Implement async/error handling
- Export function to `app.py`

#### 3. **New Data Source**
- Update `stac_service.py`
- Add query logic
- Merge results

#### 4. **New AI Model**
- Create service file
- Implement `generate_text()`
- Update `app.py` imports

---

## 🎨 UI/UX Flow

### Initial Load
1. Title: "Inspect Geospatial Data for ESG"
2. Sidebar with search filters (pre-filled defaults)
3. Empty main area

### Search Triggered
1. Show spinner: "Searching for relevant data collections..."
2. Process: Geocoding → STAC search → ESG topics
3. Show error if location not found

### Results Display
**Step 1: ESG Risk Profile**
- Tabbed interface with ESG topics
- Expandable metrics for each topic

**Step 2: Geospatial Data**
- Left: Interactive map with bounding box
- Right: Collection info (Summary + Detailed views)

**Step 3: ESG Insights**
- AI-generated text analysis
- Based on location, sector, subsector, collections

---

## 🔐 Security Considerations

### Environment Variables
- API keys in `.env` file (not committed)
- Loaded via `python-dotenv`
- Required keys:
  - `OPENAI_API_KEY`
  - `ANTHROPIC_API_KEY`
  - `GOOGLE_API_KEY`

### Input Validation
- Geocoding validates location exists
- Date range validation (start < end)
- Bounding box validation (min < max)

### Error Handling
- All API calls wrapped in try-catch
- User-friendly error messages
- Detailed logging for debugging

---

## 📈 Performance Considerations

### Caching Opportunities
- STAC collection metadata (rarely changes)
- Geocoding results (cache location → bbox)
- SASB standards (Excel file)

### Optimization Points
- Lazy loading of AI clients
- Parallel STAC searches (if multiple catalogs)
- Progressive rendering of results

### Current Limitations
- STAC search scans all collections (could be slow)
- AI generation is synchronous (blocking)
- No pagination for large results

---

## 🎯 Future Enhancement Areas

### Short-term
- Add more AI models
- Improve map interactions
- Add export functionality (PDF reports)

### Medium-term
- Real-time data updates
- Historical trend analysis
- Multi-location comparison

### Long-term
- Machine learning risk prediction
- Benchmarking against industry peers
- Integration with financial data

---

## 📝 Code Quality Patterns

### Function Signatures
```python
def function_name(param: Type) -> ReturnType:
    """Docstring describing function."""
    # Implementation
```

### Error Handling
```python
try:
    result = operation()
except SpecificError as e:
    logger.error(f"Context: {str(e)}")
    raise
except Exception as e:
    logger.error(f"Unexpected: {str(e)}")
    st.error("User-friendly message")
```

### Type Hints
```python
from typing import List, Dict, Any, Optional

def process_data(items: List[Dict[str, Any]]) -> Optional[str]:
    # Implementation
```

---

This architecture provides a solid foundation for building additional features while maintaining code quality and separation of concerns.

