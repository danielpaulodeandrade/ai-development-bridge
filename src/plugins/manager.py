import os
import importlib.util
import sys
from src.workflow_engine.tools import ToolRegistry

class PluginManager:
    """
    Carrega plugins dinamicamente de um diretório.
    """
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def load_plugins(self, plugins_dir: str) -> None:
        """
        Varre o diretório, carrega os arquivos .py e chama a função setup(registry) se existir.
        """
        if not os.path.isdir(plugins_dir):
            return

        for filename in os.listdir(plugins_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = f"ai_bridge_plugin_{filename[:-3]}"
                file_path = os.path.join(plugins_dir, filename)
                
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    try:
                        spec.loader.exec_module(module)
                        if hasattr(module, 'setup') and callable(getattr(module, 'setup')):
                            module.setup(self.registry)
                    except Exception as e:
                        # Falhas em plugins não devem quebrar a aplicação principal
                        pass
