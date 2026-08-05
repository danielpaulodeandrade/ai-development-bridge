import pytest
import asyncio
from src.browser_automation.browser_daemon import BrowserDaemon

def test_browser_daemon_singleton():
    """Testa se o BrowserDaemon eh realmente um Singleton"""
    async def run_test():
        daemon1 = await BrowserDaemon.get_instance(headless=True)
        daemon2 = await BrowserDaemon.get_instance(headless=True)
        
        assert daemon1 is daemon2
        
        # Clean up
        await daemon1.stop()
        
    asyncio.run(run_test())

def test_browser_daemon_navigation():
    """Testa se consegue instanciar e navegar para uma url"""
    async def run_test():
        daemon = await BrowserDaemon.get_instance(headless=True)
        
        page = await daemon.navigate("https://example.com")
        assert page is not None
        assert "example.com" in page.url
        
        # Se navegar para a mesma url, nao deve recarregar a pagina inteira
        page2 = await daemon.navigate("https://example.com")
        assert page is page2
        
        await daemon.stop()
        
    asyncio.run(run_test())
