import pytest
import asyncio
from src.workers.trend_discovery import TrendDiscoveryWorker, Trend
from src.provider_system.base import BaseProvider
from src.provider_system.models import ProviderRequest, ProviderResponse

class DummyProvider(BaseProvider):
    async def send_request(self, request: ProviderRequest) -> ProviderResponse:
        assert "AI" in request.prompt
        return ProviderResponse(raw_response="ok")

def test_trend_discovery_worker():
    provider = DummyProvider()
    worker = TrendDiscoveryWorker(provider)
    
    async def run():
        trends = await worker.discover_trends("AI")
        assert len(trends) == 2
        assert "Trend 1 about AI" in trends[0].topic
        assert trends[0].relevance_score == 95
        
    asyncio.run(run())
