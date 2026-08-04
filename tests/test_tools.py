import pytest
import asyncio
from src.workflow_engine.tools import BaseTool, ToolResult, ToolRegistry

class DummyTool(BaseTool):
    @property
    def name(self) -> str:
        return "dummy_tool"
        
    @property
    def description(self) -> str:
        return "A simple dummy tool for testing"
        
    async def execute(self, param="ok", **kwargs) -> ToolResult:
        if param == "error":
            return ToolResult(success=False, error="Dummy error")
        return ToolResult(success=True, data=param)

def test_tool_registry_and_execution():
    registry = ToolRegistry()
    tool = DummyTool()
    
    # Test register
    registry.register(tool)
    
    # Test duplicate register
    with pytest.raises(ValueError):
        registry.register(tool)
        
    # Test get tool
    fetched_tool = registry.get_tool("dummy_tool")
    assert fetched_tool.name == "dummy_tool"
    
    # Test list
    tools_list = registry.list_tools()
    assert "dummy_tool" in tools_list
    assert tools_list["dummy_tool"] == "A simple dummy tool for testing"
    
    # Test execution
    async def run_exec():
        res1 = await fetched_tool.execute(param="test")
        assert res1.success is True
        assert res1.data == "test"
        
        res2 = await fetched_tool.execute(param="error")
        assert res2.success is False
        assert res2.error == "Dummy error"
        
    asyncio.run(run_exec())
