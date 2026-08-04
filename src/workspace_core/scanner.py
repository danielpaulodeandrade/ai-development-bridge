import os
from pydantic import BaseModel
from typing import List
from datetime import datetime

from src.workspace_core.project_manager import ProjectManager

class FileMeta(BaseModel):
    """Metadados extraídos de um arquivo no workspace."""
    path: str
    size_bytes: int
    extension: str
    last_modified: datetime

class WorkspaceScanner:
    """Responsável por varrer o workspace e extrair metadados estáticos dos arquivos."""
    
    def __init__(self, project_manager: ProjectManager):
        self.project_manager = project_manager

    def scan(self) -> List[FileMeta]:
        """
        Escaneia todos os recursos válidos do projeto e retorna seus metadados.
        """
        files = self.project_manager.list_resources()
        metadata_list = []

        for rel_path in files:
            full_path = os.path.join(self.project_manager.root_path, rel_path)
            if not os.path.exists(full_path):
                continue
                
            try:
                stat = os.stat(full_path)
                _, ext = os.path.splitext(rel_path)
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                
                meta = FileMeta(
                    path=rel_path.replace("\\", "/"),
                    size_bytes=stat.st_size,
                    extension=ext.lower(),
                    last_modified=mod_time
                )
                metadata_list.append(meta)
            except OSError:
                # Caso o arquivo esteja bloqueado ou não possa ser lido
                pass
            
        return metadata_list
