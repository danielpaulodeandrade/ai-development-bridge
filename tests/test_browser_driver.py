import pytest
import asyncio
from src.browser_driver.base import BrowserDriver, BrowserSession
from src.browser_driver.factory import BrowserDriverFactory

class MockBrowserDriver(BrowserDriver):
    @property
    def provider_name(self) -> str:
        return "mock_provider"

    async def start_session(self) -> BrowserSession:
        return BrowserSession(session_id="mock_123", status="active")

    async def execute_action(self, action: str, **kwargs) -> dict:
        return {"result": f"action {action} executed"}

    async def close_session(self, session_id: str) -> None:
        pass

def test_browser_driver_factory():
    factory = BrowserDriverFactory()
    
    # Testa erro ao pedir provider inexistente
    with pytest.raises(ValueError):
        factory.get_driver("unknown")
        
    # Registra o mock
    factory.register_driver(MockBrowserDriver)
    
    # Resgata o mock
    driver = factory.get_driver("mock_provider")
    assert isinstance(driver, MockBrowserDriver)
    assert driver.provider_name == "mock_provider"
    
def test_browser_driver_execution():
    driver = MockBrowserDriver()
    
    async def run():
        session = await driver.start_session()
        assert session.session_id == "mock_123"
        
        action_res = await driver.execute_action("click", target="button")
        assert action_res["result"] == "action click executed"
        
        await driver.close_session(session.session_id)
        
    asyncio.run(run())
