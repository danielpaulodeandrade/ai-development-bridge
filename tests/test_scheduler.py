import asyncio
import pytest
from src.workflow_engine.scheduler import TaskScheduler
from src.workflow_engine.queue import TaskQueueManager
from src.workflow_engine.orchestrator import WorkflowOrchestrator
from src.workspace_core.project_manager import ProjectManager
from src.provider_system.models import ProviderRequest, ProviderResponse
from src.provider_system.base import BaseProvider

class DummyProvider(BaseProvider):
    async def send_request(self, request: ProviderRequest) -> ProviderResponse:
        return ProviderResponse(raw_response="ok")

def test_scheduler_delayed_task(tmp_path):
    pm = ProjectManager(str(tmp_path))
    provider = DummyProvider()
    orchestrator = WorkflowOrchestrator(pm, provider)
    queue_manager = TaskQueueManager(orchestrator)
    scheduler = TaskScheduler(queue_manager)
    
    async def run():
        # Agenda uma tarefa para rodar em 0.1s
        scheduler.schedule_at(0.1, "delayed_1", "delayed prompt")
        
        # A fila deve estar vazia inicialmente
        assert queue_manager.queue.qsize() == 0
        
        # Espera tempo suficiente para a tarefa disparar
        await asyncio.sleep(0.15)
        
        # A fila agora deve ter a tarefa
        assert queue_manager.queue.qsize() == 1
        item = await queue_manager.queue.get()
        assert item == ("delayed_1", "delayed prompt")
        
        scheduler.cancel_all()
        
    asyncio.run(run())
