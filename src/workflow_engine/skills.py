import os
import asyncio
from src.workflow_engine.tools import BaseTool, ToolResult

class ReadFileSkill(BaseTool):
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Lê o conteúdo de um arquivo do sistema em texto"

    def _read_sync(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    async def execute(self, file_path: str, **kwargs) -> ToolResult:
        if not os.path.exists(file_path):
            return ToolResult(success=False, error=f"Arquivo não encontrado: {file_path}")
        
        try:
            content = await asyncio.to_thread(self._read_sync, file_path)
            return ToolResult(success=True, data=content)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class WriteFileSkill(BaseTool):
    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Sobrescreve ou cria um arquivo com o conteúdo fornecido"

    def _write_sync(self, file_path: str, content: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    async def execute(self, file_path: str, content: str, **kwargs) -> ToolResult:
        try:
            await asyncio.to_thread(self._write_sync, file_path, content)
            return ToolResult(success=True, data=f"Arquivo {file_path} escrito com sucesso")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
