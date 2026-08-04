import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from src.workspace_core.scanner import FileMeta
from src.workspace_core.size_controller import ContextChunk

class ExportRecord(BaseModel):
    timestamp: datetime
    total_chunks: int
    files: List[str]

class ContextHistory:
    """Responsável por salvar e gerenciar o histórico de exportações de contexto."""
    
    def __init__(self, history_file: str = ".bridge_history.json"):
        self.history_file = history_file

    def _load_history(self) -> Dict[str, Any]:
        """Carrega o histórico salvo."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {"exports": []}

    def _save_history(self, data: Dict[str, Any]) -> None:
        """Salva os dados no arquivo JSON."""
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def log_export(self, files: List[FileMeta], chunks: List[ContextChunk]) -> ExportRecord:
        """Registra no histórico uma nova exportação de contexto e retorna o registro."""
        data = self._load_history()
        
        record = ExportRecord(
            timestamp=datetime.now(),
            total_chunks=len(chunks),
            files=[f.path for f in files]
        )
        
        exports = data.get("exports", [])
        exports.append(record.model_dump(mode='json'))
        
        # Manter limite máximo de histórico (ex: 50 últimos exports)
        if len(exports) > 50:
            exports = exports[-50:]
            
        data["exports"] = exports
        self._save_history(data)
        
        return record
        
    def get_last_export(self) -> Optional[ExportRecord]:
        """Retorna o último registro de exportação, se houver."""
        data = self._load_history()
        exports = data.get("exports", [])
        if not exports:
            return None
            
        return ExportRecord(**exports[-1])
