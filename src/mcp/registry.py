from typing import Dict, List, Any, Union, Optional, Tuple
from .base_provider import MCPBaseProvider
import streamlit as st
import logging

logger = logging.getLogger(__name__)

class MCPRegistry:
    """
    Registry for all MCP providers.
    Manages provider registration, discovery, and access.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MCPRegistry, cls).__new__(cls)
            cls._instance._providers = {}
        return cls._instance
    
    def register_provider(self, provider: MCPBaseProvider) -> None:
        """
        Register a new MCP provider
        
        Args:
            provider: MCPBaseProvider instance
        """
        provider_name = provider.get_name()
        if provider_name in self._providers:
            logger.warning(f"Provider {provider_name} already registered. Overwriting.")
        
        self._providers[provider_name] = provider
        logger.info(f"Registered MCP provider: {provider_name}")
    
    def get_provider(self, name: str) -> Optional[MCPBaseProvider]:
        """
        Get a provider by name
        
        Args:
            name: Name of the provider
            
        Returns:
            MCPBaseProvider instance or None if not found
        """
        if name not in self._providers:
            logger.warning(f"Provider {name} not found")
            return None
        
        return self._providers[name]
    
    def list_providers(self) -> List[str]:
        """
        List all registered providers
        
        Returns:
            List of provider names
        """
        return list(self._providers.keys())
    
    def get_providers_by_capability(self, capability: str) -> List[MCPBaseProvider]:
        """
        Get all providers that support a specific capability
        
        Args:
            capability: Capability to filter by
            
        Returns:
            List of providers that support the capability
        """
        return [
            provider for provider in self._providers.values() 
            if capability in provider.get_capabilities()
        ]