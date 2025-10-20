from .base_provider import MCPBaseProvider
from .registry import MCPRegistry
from .stac_image_provider import STACImageProvider
from .esg_analysis_provider import ESGAnalysisProvider

__all__ = [
    'MCPBaseProvider', 
    'MCPRegistry',
    'STACImageProvider',
    'ESGAnalysisProvider'
]

# Initialize the registry
registry = MCPRegistry()

# Register the example provider
registry.register_provider(STACImageProvider())

# Register the ESG analysis provider (students will implement)
registry.register_provider(ESGAnalysisProvider())