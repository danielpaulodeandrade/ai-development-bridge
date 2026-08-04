from typing import Dict, Type
from src.browser_driver.base import BrowserDriver

class BrowserDriverFactory:
    """
    Fábrica responsável por criar e registrar implementações concretas do BrowserDriver.
    """
    def __init__(self):
        self._registry: Dict[str, Type[BrowserDriver]] = {}

    def register_driver(self, driver_class: Type[BrowserDriver]) -> None:
        """Registra a classe do driver pelo provider_name."""
        # Cria uma instância dummy rápida só para ler a property (se for static property não precisava, 
        # mas como definimos provider_name como abstract property, precisamos da instância)
        dummy_instance = driver_class()
        self._registry[dummy_instance.provider_name] = driver_class

    def get_driver(self, provider_name: str) -> BrowserDriver:
        """Instancia o driver requisitado."""
        if provider_name not in self._registry:
            raise ValueError(f"BrowserDriver for '{provider_name}' is not registered.")
        return self._registry[provider_name]()
