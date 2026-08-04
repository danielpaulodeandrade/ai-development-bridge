from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class ProviderRequest(BaseModel):
    prompt: str = Field(..., description="A instrução principal do usuário")
    system_prompt: Optional[str] = Field(None, description="Instruções de sistema opcionais")
    context_files: List[str] = Field(default_factory=list, description="Lista de caminhos de arquivos de contexto")
    
class ProviderResponse(BaseModel):
    raw_response: str = Field(..., description="O texto puro retornado pelo provedor")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Informações adicionais da resposta")
    status: str = Field(default="success", description="Status da resposta (success, error, etc)")
