"""
Provider System - Registry
"""
from typing import Dict, Type
from src.provider_system.base import Provider

class ProviderRegistry:
    """Registry for managing and instantiating AI Providers."""
    
    _providers: Dict[str, Type[Provider]] = {}
    _instances: Dict[str, Provider] = {}
    
    @classmethod
    def register(cls, provider_class: Type[Provider]) -> None:
        """Registers a Provider class."""
        # Instantiate temporarily to get the name, or require a class attribute?
        # We can just require the provider_name to be a property of the class/instance.
        # Best approach for dynamic resolution without instantiating everything:
        temp_instance = provider_class()
        name = temp_instance.provider_name
        cls._providers[name] = provider_class

    @classmethod
    def get_provider(cls, name: str) -> Provider:
        """
        Retrieves a singleton instance of the requested provider.
        If it's the first time, it instantiates and calls initialize().
        """
        if name not in cls._providers:
            raise ValueError(f"Provider '{name}' is not registered.")
            
        if name not in cls._instances:
            provider_class = cls._providers[name]
            instance = provider_class()
            instance.initialize()
            cls._instances[name] = instance
            
        return cls._instances[name]

    @classmethod
    def list_providers(cls) -> list[str]:
        """Returns a list of all registered provider names."""
        return list(cls._providers.keys())

    @classmethod
    def clear(cls) -> None:
        """Clears all registered providers and instances (useful for testing)."""
        cls._providers.clear()
        cls._instances.clear()
