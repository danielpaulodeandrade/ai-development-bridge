import asyncio
import pytest
from src.workflow_engine.queue import TaskQueueManager
from src.workflow_engine.orchestrator import WorkflowOrchestrator
from src.workspace_core.project_manager import ProjectManager
from src.provider_system.models import ProviderRequest, ProviderResponse
from src.provider_system.base import BaseProvider

class DummyProvider(BaseProvider):
    def __init__(self):
        self.processed_requests = []
        
    async def send_request(self, request: ProviderRequest) -> ProviderResponse:
        # Simulate slight delay to ensure async queuing works
        await asyncio.sleep(0.01)
        self.processed_requests.append(request.prompt)
        return ProviderResponse(raw_response=f"done: {request.prompt}")

def test_task_queue_manager_execution(tmp_path):
    pyproject_file = tmp_path / "pyproject.toml"
    pyproject_file.write_text("[project]\nname = 'QueueTest'")
    
    pm = ProjectManager(str(tmp_path))
    provider = DummyProvider()
    orchestrator = WorkflowOrchestrator(pm, provider)
    queue_manager = TaskQueueManager(orchestrator)
    
    async def run():
        # Enqueue multiple tasks
        await queue_manager.enqueue("task_1", "prompt 1")
        await queue_manager.enqueue("task_2", "prompt 2")
        await queue_manager.enqueue("task_3", "prompt 3")
        
        # Start worker
        await queue_manager.start_worker()
        
        # Wait for all tasks to be processed
        await queue_manager.queue.join()
        
        # Stop worker
        await queue_manager.stop_worker()
        
        assert len(provider.processed_requests) == 3
        assert provider.processed_requests == ["prompt 1", "prompt 2", "prompt 3"]

    asyncio.run(run())
