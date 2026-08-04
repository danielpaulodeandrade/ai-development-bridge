from src.workspace_core.project_manager import ProjectManager
from src.provider_system.base import BaseProvider
from src.provider_system.models import ProviderRequest, ProviderResponse

class WorkflowOrchestrator:
    """
    Orquestra o fluxo de trabalho principal:
    recebe a intenção, junta com o contexto do projeto, e aciona o provedor.
    """
    def __init__(self, project_manager: ProjectManager, provider: BaseProvider):
        self.project_manager = project_manager
        self.provider = provider

    async def execute_task(self, prompt: str) -> ProviderResponse:
        """
        Executa uma tarefa fim a fim.
        """
        metadata = self.project_manager.get_metadata()
        
        system_prompt = "Você é um assistente de desenvolvimento."
        if metadata.get("name"):
            system_prompt += f"\nVocê está trabalhando no projeto: {metadata['name']}"
            
        request = ProviderRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            context_files=self.project_manager.list_resources()
        )
        
        response = await self.provider.send_request(request)
        return response
