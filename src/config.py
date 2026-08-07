import yaml
import os
import logging

logger = logging.getLogger(__name__)

class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _get_base_dir(self):
        import sys
        if getattr(sys, 'frozen', False):
            return os.getcwd()
        return os.path.dirname(os.path.dirname(__file__))

    def _load_config(self):
        base_dir = self._get_base_dir()
        config_path = os.path.join(base_dir, "config.yaml")
        
        # Default fallback values
        self.server = {"host": "0.0.0.0", "port": 8000}
        self.browser = {"headless": False, "timeout_ms": 10000}
        self.router = {
            "default_platform": "gpt",
            "role_registry": {
                "gpt": "chatgpt",
                "gemini": "gemini",
                "claude": "claude",
                "deepseek": "deepseek"
            }
        }
        self.agent = {"workspace_dir": ""}
        
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data:
                        if "server" in data:
                            self.server.update(data["server"])
                        if "browser" in data:
                            self.browser.update(data["browser"])
                        if "router" in data:
                            self.router.update(data["router"])
                        if "agent" in data:
                            self.agent.update(data["agent"])
                logger.info("Configuração carregada de config.yaml com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao ler config.yaml: {e}. Usando valores padrão.")
        else:
            logger.warning("Arquivo config.yaml não encontrado. Usando valores padrão.")

    def get_workspace_dir(self):
        """Resolves the working directory for the agent, prioritizing env var, then config, then fallback"""
        env_dir = os.environ.get("BRIDGE_WORKSPACE_DIR")
        if env_dir and os.path.exists(env_dir):
            return env_dir
            
        config_dir = self.agent.get("workspace_dir")
        if config_dir and os.path.exists(config_dir):
            return config_dir
            
        return os.getcwd()

# Global singleton
settings = Settings()

def setup_logging():
    import sys
    if getattr(sys, 'frozen', False):
        base_dir = os.getcwd()
    else:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        
    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join(logs_dir, "bridge.log"), encoding="utf-8")
        ]
    )

setup_logging()
