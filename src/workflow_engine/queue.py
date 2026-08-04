import asyncio
from typing import Optional
from src.workflow_engine.orchestrator import WorkflowOrchestrator
from src.provider_system.models import ProviderResponse

class TaskQueueManager:
    """
    Gerencia uma fila assíncrona de requisições para evitar sobrecarga.
    """
    def __init__(self, orchestrator: WorkflowOrchestrator):
        self.orchestrator = orchestrator
        self.queue: asyncio.Queue = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None
        self._running = False

    async def enqueue(self, task_id: str, prompt: str) -> None:
        """
        Adiciona uma tarefa à fila.
        """
        await self.queue.put((task_id, prompt))

    async def start_worker(self) -> None:
        """
        Inicia o worker em background que consome a fila.
        """
        self._running = True
        self._worker_task = asyncio.create_task(self._process_queue())

    async def stop_worker(self) -> None:
        """
        Encerra o worker de forma amigável após o processamento da fila atual.
        """
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

    async def _process_queue(self) -> None:
        """
        Loop interno do worker que retira itens da fila.
        """
        while self._running:
            try:
                task_id, prompt = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
                
            try:
                # Aqui poderíamos armazenar o resultado ou emitir um evento
                # Para M1-006, apenas processamos via orquestrador
                response = await self.orchestrator.execute_task(prompt)
            except Exception as e:
                # Tratar falhas silenciosamente ou com log no futuro
                pass
            finally:
                self.queue.task_done()
