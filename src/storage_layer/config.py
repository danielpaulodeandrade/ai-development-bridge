import os
import yaml
from typing import Any, Optional, Dict

class ConfigManager:
    """
    Gerencia a configuração central do AI Workspace Bridge.
    Carrega, acessa e salva configurações em um arquivo YAML local.
    """
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Carrega a configuração do arquivo para a memória."""
        if not os.path.exists(self.config_path):
            self._config = {}
            return

        with open(self.config_path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
                self._config = data if isinstance(data, dict) else {}
            except yaml.YAMLError:
                self._config = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Obtém o valor de uma chave na configuração."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Define o valor de uma chave na configuração em memória."""
        self._config[key] = value

    def save(self) -> None:
        """Persiste a configuração atual no arquivo YAML."""
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self._config, f, default_flow_style=False, allow_unicode=True)

# Instância centralizada oficial para uso nos outros módulos
config = ConfigManager()
