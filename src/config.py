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

    def _load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
        
        # Default fallback values
        self.server = {"host": "0.0.0.0", "port": 8000}
        self.browser = {"headless": False, "timeout_ms": 10000}
        self.router = {
            "default_platform": "gemini",
            "role_registry": {
                "architect": "chatgpt",
                "coder": "claude",
                "reviewer": "gemini"
            }
        }
        
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
                logger.info("Configuração carregada de config.yaml com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao ler config.yaml: {e}. Usando valores padrão.")
        else:
            logger.warning("Arquivo config.yaml não encontrado. Usando valores padrão.")

# Global singleton
settings = Settings()

def setup_logging():
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
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
