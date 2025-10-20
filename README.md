# 🌍 ESG Geospatial Data Inspector MVP

A comprehensive web application that combines **ESG (Environmental, Social, Governance) analysis** with **geospatial data exploration** to help companies assess ESG risks and opportunities using satellite imagery and spatial data.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Model Context Protocol (MCP) Architecture](#model-context-protocol-mcp-architecture)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Deployment](#deployment)
- [Team Development Guide](#team-development-guide)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

## 🎯 Project Overview

This MVP addresses the growing need for **data-driven ESG assessment** by combining:
- **Industry-standard ESG frameworks** (SASB standards)
- **Professional geospatial data sources** (Microsoft Planetary Computer)
- **AI-powered insights** (OpenAI GPT-3.5-turbo)
- **Interactive mapping** and data visualization

### Business Value
- **ESG Compliance**: Meet regulatory and investor ESG reporting requirements
- **Risk Management**: Identify material ESG risks before financial impact
- **Data-Driven Decisions**: Leverage satellite imagery for ESG insights
- **Industry-Specific Analysis**: Tailored assessment for 10 sectors and 77 subsectors

## ✨ Features

### 🔍 ESG Risk Assessment
- **Industry Classification**: 10 major sectors with detailed subsectors
- **SASB Integration**: Maps to specific ESG disclosure topics and metrics
- **Risk Profiling**: Identifies material ESG risks impacting financial performance

### 🗺️ Geospatial Data Discovery
- **Location-Based Search**: Geocoding with bounding box generation
- **Temporal Filtering**: Date range validation and filtering
- **STAC Collection Search**: Spatial and temporal intersection analysis
- **Data Collection Metadata**: Comprehensive dataset information


### 🎨 Interactive Mapping
- **Area Visualization**: Bounding box display with search area highlighting
- **Geographic Context**: US regions, cities, and spatial boundaries
- **Interactive Features**: Zoom, pan, and geographic information layers

### 🤖 AI-Powered Insights
- **Contextual Analysis**: Sector and subsector-specific ESG analysis
- **Data-Driven Recommendations**: AI-generated insights based on available data
- **ESG Opportunity Identification**: Risk assessment and strategic recommendations

## 🛠️ Technology Stack

### Frontend & Framework
- **Streamlit** - Main web framework with interactive UI
- **Folium** - Interactive mapping capabilities
- **Streamlit-Folium** - Integration between Streamlit and Folium

### Backend Services
- **STAC Service** - Microsoft Planetary Computer STAC API integration
- **Geocoding Service** - Nominatim for location-to-coordinates conversion
- **Gemini Service** - Google Gemini 1.5 Flash for ESG insights generation
- **OpenAI Service** - GPT-3.5-turbo for ESG insights generation
- **Geospatial Data Service** - Raster/vector data processing

### Data Sources
- **Microsoft Planetary Computer** - Primary STAC catalog for satellite imagery
- **SASB Standards** - Industry-specific ESG metrics and disclosure topics
- **US Geographic Data** - Cities, regions, and spatial boundaries

### Deployment & Infrastructure
- **Docker** - Containerized application
- **Google Cloud Platform** - Cloud Run deployment
- **Cloud Build** - CI/CD pipeline

## 📁 Project Structure

```
streamlit/
├── src/                          # Main application source code
│   ├── app.py                   # Main Streamlit application
│   ├── components/              # UI components
│   │   ├── sidebar.py          # Sidebar with search filters
│   │   └── maps.py             # Interactive mapping components
│   ├── services/                # Business logic services
│   │   ├── stac_service.py     # STAC API integration
│   │   ├── geocoding.py        # Location services
│   │   ├── openai_service.py   # AI insights generation
│   │   └── geospatial_data_service.py  # Data processing
│   ├── config/                  # Configuration files
│   │   └── sasb_sectors.py     # Industry sector definitions
│   ├── utils/                   # Utility functions
│   │   ├── date_utils.py       # Date handling utilities
│   │   ├── spatial_utils.py    # Spatial calculations
│   │   └── extract_subsector_info.py  # SASB data extraction
│   └── data/                    # Static data files
│       ├── SASB standard.xlsx   # ESG standards database
│       ├── us_cities.csv        # US cities data
│       └── us_regions.geojson  # US geographic boundaries
├── Dockerfile                   # Docker container configuration
├── docker-compose.yml          # Local development setup
├── requirements.txt             # Python dependencies
├── cloudbuild.yaml             # GCP Cloud Build configuration
├── deploy-script.sh            # Deployment automation script
└── README.md                   # This file
```

## 🧩 Model Context Protocol (MCP) Architecture

The application uses the **Model Context Protocol (MCP)** framework to connect satellite data analysis with AI-powered ESG insights.

### Architecture Flow

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ↓
┌─────────────────┐
│  Streamlit App  │
└─────┬───────────┘
      │
      ↓
┌───────────────────┐
│  MCP Framework    │
│  ┌──────────────┐ │
│  │ STAC Provider│ │ → Fetch satellite data
│  └──────┬───────┘ │
│         ↓         │
│  ┌──────────────┐ │
│  │ ESG Provider │ │ → Analyze data (NDVI, etc.)
│  └──────┬───────┘ │
└─────────┼─────────┘
          │ Real analysis results
          ↓
    ┌────────────┐
    │ LLM (GPT)  │ → Generate insights from ACTUAL data
    └────────────┘
```

### How It Works

1. **User Input**: Location, sector, and subsector selection
2. **Data Retrieval**: STAC Provider fetches satellite imagery from Microsoft Planetary Computer
3. **ESG Analysis**: ESG Provider processes satellite data to calculate environmental metrics
4. **AI Insights**: LLM receives real analysis results and generates actionable ESG recommendations

### MCP Components

- **`src/mcp/base_provider.py`**: Abstract interface for all providers
- **`src/mcp/stac_image_provider.py`**: Satellite imagery retrieval (✅ Implemented)
- **`src/mcp/esg_analysis_provider.py`**: ESG metrics calculation (🚧 Student task)
- **`src/mcp/registry.py`**: Provider discovery and management

For students: See [STUDENT_GUIDE.md](STUDENT_GUIDE.md) for implementation details.

## 🚀 Getting Started

### 🎯 Quick Start for Students

1. **Clone and Setup** (5 minutes)
   ```bash
   git clone <your-repo-url>
   cd streamlit
   copy env_template.txt .env  # Windows
   # OR
   cp env_template.txt .env    # macOS/Linux
   ```

2. **Get API Keys** (10 minutes)
   - Ask your instructor for shared API keys, OR
   - Sign up for free API credits at [OpenAI](https://platform.openai.com/) 

3. **Edit .env file** (2 minutes)
   - Open `.env` in any text editor
   - Replace `your_key` with actual API keys

4. **Run the app** (3 minutes)
   ```bash
   pip install -r requirements.txt
   streamlit run src/app.py
   ```

### Prerequisites
- **Python 3.9+** (recommended: 3.9 or 3.10)
- **Docker** (for containerized deployment)
- **Google Cloud Platform** account (for production deployment)
- **API keys** for OpenAI and/or Anthropic (for AI insights generation)

### Environment Variables
This project uses environment variables for configuration. Follow these steps to set up your environment:

1. **Copy the template file:**
   ```bash
   # On Windows
   copy env_template.txt .env
   
   # On macOS/Linux
   cp env_template.txt .env
   ```

2. **Edit the `.env` file** with your actual API keys and configuration:
   ```bash
   # Required: OpenAI API Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Required: Anthropic API Configuration  
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   
   # Streamlit Configuration (optional - defaults are set)
   STREAMLIT_SERVER_PORT=8080
   STREAMLIT_SERVER_ADDRESS=0.0.0.0
   STREAMLIT_SERVER_HEADLESS=true
   STREAMLIT_THEME_BASE=light
   STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
   ```

3. **Get your API keys:**
   - **OpenAI API Key**: Sign up at [OpenAI Platform](https://platform.openai.com/) and create an API key
   - **Anthropic API Key**: Sign up at [Anthropic Console](https://console.anthropic.com/) and create an API key

4. **Important**: Never commit your `.env` file to version control! It's already in `.gitignore` to prevent accidental commits.

**Note for Students**: If you don't have API keys yet, you can still run the application locally, but the AI insights generation features won't work. Ask your instructor or team lead for shared API keys for development purposes.

## 💻 Development Setup

### Option 1: Local Python Environment

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd streamlit
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run src/app.py
   ```

### Option 2: Docker Development

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - Open your browser to `http://localhost:8080`

### Option 3: Docker Only

1. **Build the Docker image**
   ```bash
   docker build -t stac-esg-app .
   ```

2. **Run the container**
   ```bash
   docker run -p 8080:8080 --env-file .env stac-esg-app
   ```

## 🚀 Deployment

### Google Cloud Platform (Recommended)

1. **Set up GCP project**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Enable required APIs**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   ```

3. **Deploy using the script**
   ```bash
   chmod +x deploy-script.sh
   ./deploy-script.sh
   ```

### Manual Deployment

1. **Build and push to Container Registry**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/stac-esg-app
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy stac-esg-app \
       --image gcr.io/PROJECT_ID/stac-esg-app \
       --platform managed \
       --region us-central1 \
       --allow-unauthenticated
   ```

## 👥 Team Development Guide

### Development Workflow

1. **Feature Development**
   - Create feature branches: `git checkout -b feature/feature-name`
   - Implement changes following the project structure
   - Test locally before committing
   - Create pull requests for review

2. **Code Organization**
   - **Frontend Components**: Add new UI elements in `src/components/`
   - **Business Logic**: Implement new services in `src/services/`
   - **Utilities**: Add helper functions in `src/utils/`
   - **Configuration**: Update settings in `src/config/`

3. **Testing Strategy**
   - Unit tests for utility functions
   - Integration tests for services
   - End-to-end tests for user workflows

### Team Roles & Responsibilities

#### **Frontend Developer (2-3 students)**
- **Focus**: Streamlit UI components, user experience, responsive design
- **Key Files**: `src/components/`, `src/app.py`
- **Skills**: Streamlit, HTML/CSS, UI/UX design

#### **Backend Developer (2-3 students)**
- **Focus**: API integrations, data processing, business logic
- **Key Files**: `src/services/`, `src/utils/`
- **Skills**: Python, API development, data processing

#### **Data Engineer (1-2 students)**
- **Focus**: Data pipelines, STAC API optimization, data validation
- **Key Files**: `src/services/stac_service.py`, `src/services/geospatial_data_service.py`
- **Skills**: Geospatial data, STAC APIs, data engineering

#### **DevOps Engineer (1-2 students)**
- **Focus**: Deployment, CI/CD, infrastructure, monitoring
- **Key Files**: `Dockerfile`, `cloudbuild.yaml`, `deploy-script.sh`
- **Skills**: Docker, GCP, CI/CD, monitoring

### Environment Setup for Students

1. **First-time Setup**
   ```bash
   # Clone the repository
   git clone <your-repo-url>
   cd streamlit
   
   # Copy environment template
   copy env_template.txt .env  # Windows
   # OR
   cp env_template.txt .env    # macOS/Linux
   
   # Edit .env file with your API keys
   # Use a text editor like VS Code, Notepad++, or nano
   ```

2. **API Key Management**
   - **Individual Development**: Use your own API keys for personal development
   - **Team Development**: Coordinate with your team lead for shared API keys
   - **Class Projects**: Your instructor may provide shared API keys for the entire class

3. **Environment File Security**
   - The `.env` file is automatically ignored by Git
   - Never share your API keys in chat, emails, or code reviews
   - If you accidentally commit API keys, immediately rotate them

### Development Best Practices

1. **Code Style**
   - Follow PEP 8 Python style guide
   - Use type hints for function parameters and return values
   - Write comprehensive docstrings for all functions

2. **Error Handling**
   - Implement proper exception handling
   - Provide meaningful error messages to users
   - Log errors for debugging

3. **Performance**
   - Cache expensive operations (STAC queries, geocoding)
   - Optimize database queries and API calls
   - Implement lazy loading for large datasets

4. **Security**
   - Never commit API keys or sensitive data
   - Validate all user inputs
   - Implement rate limiting for external APIs

## 📚 API Documentation

### STAC Service
- **`search_stac_collections(bbox_filter, temporal_filter)`**: Search for available data collections
- **`get_collection_info(collection)`**: Extract metadata from STAC collections
- **`get_collection_assets(collection)`**: Get available data assets

### Geocoding Service
- **`get_bounding_box(location)`**: Convert location names to bounding box coordinates

### OpenAI Service
- **`generate_text(prompt, sector, subsector)`**: Generate ESG insights using AI

### Geospatial Data Service
- **`fetch_geospatial_data(collection_id, bbox, time_range)`**: Fetch actual data from STAC collections
- **`load_and_display_data(item, url, data_type)`**: Process and visualize geospatial data

## 🔧 Contributing

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

### Pull Request Guidelines

- **Clear description** of what the PR accomplishes
- **Screenshots** for UI changes
- **Test coverage** for new functionality
- **Documentation updates** if needed

### Code Review Process

1. **Self-review** your code before submitting
2. **Peer review** by at least one team member
3. **Address feedback** and make necessary changes
4. **Merge** after approval

## 🐛 Troubleshooting

### Common Issues

#### **Google Gemini API Errors**
- Verify your API key is correct
- Check API usage limits and billing
- Ensure the API key has proper permissions

#### **STAC API Issues**
- Verify internet connectivity
- Check if Microsoft Planetary Computer is accessible
- Review API rate limits

#### **Geocoding Failures**
- Ensure location names are specific and accurate
- Check Nominatim service availability
- Verify location format (city, country)

#### **Docker Issues**
- Ensure Docker is running
- Check port availability (8080)
- Verify environment variables are set

#### **Streamlit Errors**
- Check Python version compatibility
- Verify all dependencies are installed
- Review Streamlit configuration

#### **Environment Setup Issues**
- Ensure `.env` file exists in the root directory
- Verify API keys are correctly formatted (no extra spaces or quotes)
- Check that `env_template.txt` was copied to `.env` (not just renamed)
- Confirm API keys are valid and have sufficient credits
- For Windows users: Use `copy` command, not `cp`

### Getting Help

1. **Check the logs** for detailed error messages
2. **Review the documentation** for common solutions
3. **Search existing issues** in the repository
4. **Create a new issue** with detailed information

## 📈 Future Enhancements

### Short-term (Next 2-4 weeks)
- [ ] Enhanced error handling and user feedback
- [ ] Data validation improvements
- [ ] Performance optimization and caching
- [ ] Mobile-responsive design improvements

### Medium-term (Next 1-2 months)
- [ ] Advanced analytics and statistical analysis
- [ ] Export capabilities (PDF reports, data downloads)
- [ ] User management and role-based access
- [ ] Historical ESG performance tracking

### Long-term (Next 3-6 months)
- [ ] Comparative industry benchmarking
- [ ] Machine learning for ESG risk prediction
- [ ] Integration with additional data sources
- [ ] Advanced visualization and dashboard features

## 📞 Support & Contact

- **Project Lead**: [Your Name]
- **Team Repository**: [GitHub Repository URL]
- **Documentation**: [Project Wiki/Docs URL]
- **Issue Tracker**: [GitHub Issues URL]

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Happy coding! 🚀**

*Built with ❤️ by the ESG Geospatial Data Inspector Team*
