import os
import pytest
from src.workflow_engine.tools import ToolRegistry
from src.plugins.manager import PluginManager

def test_plugin_manager_loading(tmp_path):
    registry = ToolRegistry()
    manager = PluginManager(registry)
    
    # Criar um plugin temporário
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    
    plugin_file = plugin_dir / "my_plugin.py"
    plugin_file.write_text('''
from src.workflow_engine.tools import BaseTool, ToolResult

class MyPluginTool(BaseTool):
    @property
    def name(self): return "plugin_tool"
    @property
    def description(self): return "Tool from plugin"
    async def execute(self, **kwargs): return ToolResult(success=True)

def setup(registry):
    registry.register(MyPluginTool())
''')

    # Carregar plugins
    manager.load_plugins(str(plugin_dir))
    
    # Verificar se a tool foi registrada
    assert "plugin_tool" in registry.list_tools()
