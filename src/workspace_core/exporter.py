import os
from typing import List
from src.workspace_core.size_controller import ContextChunk

class MarkdownExporter:
    """Responsável por salvar os chunks do contexto gerados em arquivos físicos no disco."""
    
    def __init__(self, output_dir: str = "docs/generated/context"):
        self.output_dir = output_dir

    def export(self, context_id: str, chunks: List[ContextChunk]) -> List[str]:
        """Salva a lista de chunks em arquivos e retorna os caminhos gerados."""
        if not chunks:
            return []
            
        target_dir = os.path.join(self.output_dir, context_id)
        os.makedirs(target_dir, exist_ok=True)
        
        saved_files = []
        for chunk in chunks:
            # Ex: M1-024-part1.md
            file_name = f"{context_id}-part{chunk.index}.md"
            file_path = os.path.join(target_dir, file_name)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(chunk.text_content)
                
            # Troca as barras para garantir que fique sempre legível (Linux/Windows)
            saved_files.append(file_path.replace("\\", "/"))
            
        return saved_files
