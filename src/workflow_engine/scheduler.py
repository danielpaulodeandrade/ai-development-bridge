import asyncio
from typing import Optional, Callable, Awaitable
from src.workflow_engine.queue import TaskQueueManager

class TaskScheduler:
    """
    Agendador simples para disparar tarefas recorrentes ou atrasadas
    e injetá-las na fila de execução principal.
    """
    def __init__(self, queue_manager: TaskQueueManager):
        self.queue_manager = queue_manager
        self._tasks = []

    def schedule_at(self, delay_seconds: float, task_id: str, prompt: str) -> asyncio.Task:
        """
        Agenda uma tarefa para rodar apenas uma vez após X segundos.
        """
        async def delayed_task():
            await asyncio.sleep(delay_seconds)
            await self.queue_manager.enqueue(task_id, prompt)
            
        task = asyncio.create_task(delayed_task())
        self._tasks.append(task)
        return task

    def schedule_interval(self, interval_seconds: float, task_id_prefix: str, prompt: str) -> asyncio.Task:
        """
        Agenda uma tarefa para rodar repetidamente a cada X segundos.
        """
        async def interval_task():
            counter = 1
            while True:
                await asyncio.sleep(interval_seconds)
                current_task_id = f"{task_id_prefix}_{counter}"
                await self.queue_manager.enqueue(current_task_id, prompt)
                counter += 1
                
        task = asyncio.create_task(interval_task())
        self._tasks.append(task)
        return task

    def cancel_all(self):
        """
        Cancela todos os agendamentos pendentes.
        """
        for task in self._tasks:
            if not task.done():
                task.cancel()
