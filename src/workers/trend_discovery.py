from typing import List, Dict, Any
from pydantic import BaseModel
from src.provider_system.base import BaseProvider
from src.provider_system.models import ProviderRequest

class Trend(BaseModel):
    topic: str
    relevance_score: int
    context: str

class TrendDiscoveryWorker:
    """
    Agente responsável por identificar tendências de mercado ou tópicos quentes.
    """
    def __init__(self, provider: BaseProvider):
        self.provider = provider

    async def discover_trends(self, theme: str) -> List[Trend]:
        """
        Invoque o modelo de IA (via provider) para descobrir tendências sobre um tema.
        """
        system_prompt = (
            "Você é um pesquisador de mercado especialista. "
            "Sua tarefa é retornar tendências sobre o tema solicitado."
        )
        request = ProviderRequest(
            prompt=f"Quais são as principais tendências atuais sobre {theme}?",
            system_prompt=system_prompt,
            context_files=[]
        )
        
        response = await self.provider.send_request(request)
        
        # Em uma implementação real acoplada a um LLM de verdade, faríamos um JSON parse da resposta.
        # Para a Milestone 2 de fundação do Worker, retornamos um parse fixo em cima do retorno.
        trends = [
            Trend(topic=f"Trend 1 about {theme}", relevance_score=95, context="Context 1"),
            Trend(topic=f"Trend 2 about {theme}", relevance_score=85, context="Context 2"),
        ]
        return trends
