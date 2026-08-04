import asyncio
import pytest
from src.workflow_engine.orchestrator import WorkflowOrchestrator
from src.workspace_core.project_manager import ProjectManager
from src.provider_system.models import ProviderRequest, ProviderResponse
from src.provider_system.base import BaseProvider

class DummyProvider(BaseProvider):
    def __init__(self):
        self.last_request = None
        
    async def send_request(self, request: ProviderRequest) -> ProviderResponse:
        self.last_request = request
        return ProviderResponse(raw_response="ok")

def test_workflow_orchestrator_execution(tmp_path):
    pyproject_file = tmp_path / "pyproject.toml"
    pyproject_file.write_text("[project]\nname = 'TestProject'")
    
    pm = ProjectManager(str(tmp_path))
    provider = DummyProvider()
    orchestrator = WorkflowOrchestrator(pm, provider)
    
    async def run():
        response = await orchestrator.execute_task("Crie uma função soma")
        assert response.raw_response == "ok"
        assert provider.last_request is not None
        assert provider.last_request.prompt == "Crie uma função soma"
        assert "TestProject" in provider.last_request.system_prompt
        
    asyncio.run(run())
