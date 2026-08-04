from typing import List, Set, Optional
from pydantic import BaseModel, Field
from src.workspace_core.scanner import FileMeta

class SelectionRules(BaseModel):
    max_size_bytes: int = Field(
        default=500_000, 
        description="Tamanho máximo de um arquivo em bytes para inclusão."
    )
    allowed_extensions: Optional[Set[str]] = Field(
        default=None, 
        description="Se definido, permite apenas estas extensões (ex: {'.py', '.md'})."
    )
    ignored_paths: Set[str] = Field(
        default_factory=set, 
        description="Pastas ou arquivos específicos para ignorar."
    )

class FileSelector:
    """Filtra os arquivos escaneados com base em regras de negócio para formar o contexto."""
    def __init__(self, rules: SelectionRules = None):
        self.rules = rules or SelectionRules()
        
    def select(self, files: List[FileMeta]) -> List[FileMeta]:
        """Filtra a lista de arquivos com base nas regras de seleção."""
        selected = []
        for file in files:
            if file.size_bytes > self.rules.max_size_bytes:
                continue
                
            if self.rules.allowed_extensions is not None:
                if file.extension not in self.rules.allowed_extensions:
                    continue
                    
            is_ignored = False
            for ignored in self.rules.ignored_paths:
                if ignored in file.path:
                    is_ignored = True
                    break
            
            if is_ignored:
                continue
                
            selected.append(file)
            
        return selected
