from abc import ABC, abstractmethod
from typing import Dict, List, Any, Union, Optional, Tuple

class MCPBaseProvider(ABC):
    """
    Base abstract class for all Model Context Protocol providers.
    Each provider implements specific geospatial data retrieval and analysis functionality.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the provider"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return a description of what the provider does"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities this provider supports"""
        pass
    
    def is_available(self) -> bool:
        """Check if the provider is available (has required credentials, etc.)"""
        return True