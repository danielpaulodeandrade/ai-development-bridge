import os
import tomllib
from typing import Dict, Any, List

class ProjectManager:
    """
    Gerencia a representação do workspace local.
    """
    IGNORED_DIRS = {".git", ".venv", "__pycache__", "node_modules", ".pytest_cache", "docs"}

    def __init__(self, root_path: str):
        self.root_path = os.path.abspath(root_path)
        if not os.path.isdir(self.root_path):
            raise ValueError(f"Path is not a valid directory: {self.root_path}")

    def get_metadata(self) -> Dict[str, Any]:
        """
        Extrai metadados básicos se pyproject.toml existir.
        """
        pyproject_path = os.path.join(self.root_path, "pyproject.toml")
        if os.path.exists(pyproject_path):
            with open(pyproject_path, "rb") as f:
                try:
                    data = tomllib.load(f)
                    return data.get("project", {})
                except tomllib.TOMLDecodeError:
                    return {}
        return {}

    def list_resources(self) -> List[str]:
        """
        Retorna uma lista de caminhos de arquivos relativos à raiz,
        ignorando diretórios configurados.
        """
        resources = []
        for root, dirs, files in os.walk(self.root_path):
            # Remove ignored directories in-place so os.walk doesn't traverse them
            dirs[:] = [d for d in dirs if d not in self.IGNORED_DIRS]
            
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.root_path)
                # Convert backslashes to forward slashes for consistent representation
                resources.append(rel_path.replace("\\", "/"))
        return resources
