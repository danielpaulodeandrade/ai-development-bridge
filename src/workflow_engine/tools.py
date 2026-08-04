from abc import ABC, abstractmethod
from typing import Dict, Any, Type
from pydantic import BaseModel, Field

class ToolResult(BaseModel):
    success: bool = Field(..., description="Indica se a ferramenta executou com sucesso")
    data: Any = Field(None, description="O retorno da ferramenta (texto, JSON, etc)")
    error: str = Field(None, description="Mensagem de erro, se houver")

class BaseTool(ABC):
    """
    Interface base para qualquer ferramenta ou habilidade.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome único da ferramenta"""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Descrição da utilidade da ferramenta"""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Lógica de execução da ferramenta.
        """
        pass

class ToolRegistry:
    """
    Gerencia o registro e descoberta de ferramentas no sistema.
    """
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Registra uma instância de ferramenta."""
        if tool.name in self._tools:
            raise ValueError(f"A tool named {tool.name} is already registered.")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        """Busca uma ferramenta pelo nome."""
        if name not in self._tools:
            raise KeyError(f"Tool {name} not found.")
        return self._tools[name]
        
    def list_tools(self) -> Dict[str, str]:
        """Retorna as ferramentas disponíveis (nome e descrição)."""
        return {name: tool.description for name, tool in self._tools.items()}
