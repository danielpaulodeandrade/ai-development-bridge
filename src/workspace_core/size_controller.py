import os
from pydantic import BaseModel
from typing import List
from src.workspace_core.scanner import FileMeta

class ContextChunk(BaseModel):
    index: int
    total_chunks: int
    text_content: str

class SizeRules(BaseModel):
    max_chars_per_chunk: int = 12000

class ContextSizeController:
    """Responsável por juntar os arquivos selecionados e fatiá-los em chunks seguros para o LLM."""
    
    def __init__(self, rules: SizeRules = None, root_path: str = ""):
        self.rules = rules or SizeRules()
        self.root_path = root_path
        
    def _read_file_content(self, file_meta: FileMeta) -> str:
        """Lê o conteúdo do arquivo."""
        full_path = os.path.join(self.root_path, file_meta.path)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            return f"[{file_meta.path} contém binário ou encoding não suportado]"
        except OSError:
            return f"[Erro ao ler {file_meta.path}]"

    def chunk_files(self, files: List[FileMeta]) -> List[ContextChunk]:
        """
        Gera um super markdown com o conteúdo de todos os arquivos, 
        e fatia em partes respeitando a quebra de linha.
        """
        super_md_parts = []
        for f in files:
            content = self._read_file_content(f)
            super_md_parts.append(f"--- {f.path} ---\n{content}\n")
            
        full_text = "\n".join(super_md_parts)
        
        if not full_text.strip():
            return []
            
        chunks_text = []
        max_chars = self.rules.max_chars_per_chunk
        
        current_chunk = []
        current_len = 0
        
        for line in full_text.splitlines(keepends=True):
            line_len = len(line)
            
            if line_len > max_chars:
                if current_chunk:
                    chunks_text.append("".join(current_chunk))
                    current_chunk = []
                    current_len = 0
                
                # Força a fatiagem se a linha for gigante
                for i in range(0, line_len, max_chars):
                    chunks_text.append(line[i:i+max_chars])
                continue

            if current_len + line_len > max_chars:
                chunks_text.append("".join(current_chunk))
                current_chunk = [line]
                current_len = line_len
            else:
                current_chunk.append(line)
                current_len += line_len
                
        if current_chunk:
            chunks_text.append("".join(current_chunk))
            
        total_chunks = len(chunks_text)
        result = []
        for i, text in enumerate(chunks_text):
            header = ""
            if total_chunks > 1:
                if i < total_chunks - 1:
                    header = f"**[Parte {i+1}/{total_chunks}] Aguarde todas as partes para começar a analisar.**\n\n"
                else:
                    header = f"**[Parte {i+1}/{total_chunks}] Fim do contexto. Pode começar a análise.**\n\n"
                
            chunk = ContextChunk(
                index=i+1,
                total_chunks=total_chunks,
                text_content=header + text
            )
            result.append(chunk)
            
        return result
