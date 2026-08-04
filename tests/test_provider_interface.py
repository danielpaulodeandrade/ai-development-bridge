import asyncio
from src.provider_system.models import ProviderRequest, ProviderResponse
from src.provider_system.base import BaseProvider

class MockProvider(BaseProvider):
    async def send_request(self, request: ProviderRequest) -> ProviderResponse:
        return ProviderResponse(
            raw_response=f"Recebi seu prompt: {request.prompt}",
            metadata={"mocked": True}
        )

def test_mock_provider_implementation():
    async def run_test():
        provider = MockProvider()
        req = ProviderRequest(prompt="Olá Mundo", system_prompt="Aja como um assistente")
        resp = await provider.send_request(req)
        
        assert resp.status == "success"
        assert "Olá Mundo" in resp.raw_response
        assert resp.metadata.get("mocked") is True
        
    asyncio.run(run_test())
