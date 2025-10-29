"""
MCP (Model Context Protocol) Service
Provides a framework for exposing tools and data sources to AI models via MCP.

This allows AI agents to interact with:
- STAC API for geospatial data
- Geocoding services
- ESG data sources
- And other future tooling
"""

import os
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Represents an MCP tool definition."""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable
    enabled: bool = True


class MCPService:
    """
    MCP Service for exposing tools to AI models.
    
    This service provides a Python implementation of MCP functionality
    that can be used with AI agents to interact with geospatial data,
    STAC APIs, and other resources.
    """
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default MCP tools for geospatial and ESG operations."""
        
        # Register STAC search tool
        self.register_tool(
            "search_stac_collections",
            "Search for STAC collections matching spatial and temporal criteria",
            {
                "type": "object",
                "properties": {
                    "bbox": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Bounding box [min_lon, min_lat, max_lon, max_lat]"
                    },
                    "datetime": {
                        "type": "string",
                        "description": "ISO 8601 datetime range or single datetime"
                    },
                    "collections": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Collection IDs to search"
                    }
                },
                "required": ["bbox"]
            },
            self._handle_stac_search
        )
        
        # Register geocoding tool
        self.register_tool(
            "geocode_location",
            "Convert a location name to coordinates",
            {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location name or address"
                    }
                },
                "required": ["location"]
            },
            self._handle_geocode
        )
        
        # Register ESG topic extraction tool
        self.register_tool(
            "get_esg_topics",
            "Get ESG disclosure topics for a specific sector and subsector",
            {
                "type": "object",
                "properties": {
                    "subsector": {
                        "type": "string",
                        "description": "Industry subsector name"
                    }
                },
                "required": ["subsector"]
            },
            self._handle_esg_topics
        )
    
    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable,
        enabled: bool = True
    ):
        """
        Register a new MCP tool.
        
        Args:
            name: Tool name (must be unique)
            description: Human-readable description
            parameters: JSON Schema definition of parameters
            handler: Function to handle tool calls
            enabled: Whether the tool is enabled
        """
        if name in self.tools:
            logger.warning(f"Tool {name} is being overwritten")
        
        self.tools[name] = MCPTool(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
            enabled=enabled
        )
        logger.info(f"Registered MCP tool: {name}")
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available MCP tools.
        
        Returns:
            List of tool definitions
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "enabled": tool.enabled
            }
            for tool in self.tools.values()
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call an MCP tool by name with the given arguments.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool result
            
        Raises:
            ValueError: If tool doesn't exist or is disabled
        """
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        
        tool = self.tools[name]
        
        if not tool.enabled:
            raise ValueError(f"Tool {name} is disabled")
        
        logger.info(f"Calling MCP tool: {name} with args: {arguments}")
        result = tool.handler(**arguments)
        return result
    
    # Tool handlers
    
    def _handle_stac_search(self, bbox: List[float], datetime: Optional[str] = None, collections: Optional[List[str]] = None):
        """Handle STAC collection search tool calls."""
        from services.stac_service import search_stac_collections
        
        if datetime is None:
            datetime = "2020-01-01, 2025-12-31"
        
        matching_collections, collection_info = search_stac_collections(
            bbox_filter=bbox,
            temporal_filter=datetime
        )
        
        return {
            "collections": [
                {
                    "id": coll.id,
                    "title": getattr(coll, 'title', 'No title'),
                    "description": coll.description
                }
                for coll in matching_collections
            ],
            "count": len(matching_collections)
        }
    
    def _handle_geocode(self, location: str):
        """Handle geocoding tool calls."""
        from services.geocoding import get_bounding_box
        
        bbox = get_bounding_box(location)
        
        if bbox is None:
            return {"error": f"Could not find location: {location}"}
        
        center_lat = (bbox[1] + bbox[3]) / 2
        center_lon = (bbox[0] + bbox[2]) / 2
        
        return {
            "location": location,
            "coordinates": {
                "latitude": center_lat,
                "longitude": center_lon
            },
            "bounding_box": bbox
        }
    
    def _handle_esg_topics(self, subsector: str):
        """Handle ESG topics extraction tool calls."""
        from utils.extract_subsector_info import extract_subsector_info
        
        subsector_info = extract_subsector_info(
            './src/data/SASB standard.xlsx',
            subsector
        )
        
        if subsector_info is None or subsector_info.empty:
            return {"error": f"No ESG topics found for subsector: {subsector}"}
        
        topics = subsector_info[['Topic', 'Accounting Metric']].to_dict('records')
        
        return {
            "subsector": subsector,
            "topics": [
                {
                    "topic": row['Topic'],
                    "metrics": row['Accounting Metric']
                }
                for row in topics
            ],
            "count": len(topics)
        }


# Global MCP service instance
_mcp_service: Optional[MCPService] = None


def get_mcp_service() -> MCPService:
    """
    Get or create the global MCP service instance.
    
    Returns:
        MCPService instance
    """
    global _mcp_service
    if _mcp_service is None:
        _mcp_service = MCPService()
    return _mcp_service


def list_mcp_tools() -> List[Dict[str, Any]]:
    """List all available MCP tools."""
    return get_mcp_service().list_tools()

