import logging
import asyncio
import re
from bs4 import BeautifulSoup
from playwright.async_api import Page
from .browser_daemon import BrowserDaemon
from .text_feeder import TextFeeder
from src.agent.parser import AACPParser
from src.agent.file_executor import FileExecutor

logger = logging.getLogger(__name__)

class SelfHealingEngine:
    def __init__(self, daemon: BrowserDaemon):
        self.daemon = daemon
        self.feeder = TextFeeder(daemon)

    def _clean_html(self, raw_html: str) -> str:
        """Limpa o HTML para caber no prompt da IA, removendo tags pesadas e inuteis."""
        soup = BeautifulSoup(raw_html, "html.parser")
        
        # Remover tags desnecessárias
        for tag in soup(["script", "style", "svg", "path", "head", "meta", "noscript", "img", "iframe"]):
            tag.decompose()
            
        # Remover atributos muito grandes que não ajudam no parsing de layout
        for tag in soup.find_all(True):
            attrs_to_remove = ["d", "viewBox", "xmlns", "style"]
            for attr in attrs_to_remove:
                if attr in tag.attrs:
                    del tag.attrs[attr]
                    
        cleaned = soup.prettify()
        
        # Se ainda for muito grande, pegamos apenas os últimos 15000 caracteres (foco na nova mensagem)
        if len(cleaned) > 20000:
            cleaned = "... [TRUNCATED] ...\n" + cleaned[-20000:]
            
        return cleaned

    async def initiate_healing(self, platform: str, failed_selector: str) -> bool:
        """
        Inicia o protocolo de autocura:
        1. Lê o HTML e o código fonte.
        2. Envia o prompt de cura.
        3. Espera pelo AACP Patch diretamente no innerText do navegador.
        4. Aplica o patch.
        """
        logger.warning(f"Iniciando Self-Healing Engine para a plataforma {platform}. Seletor falho: {failed_selector}")
        
        if not self.daemon._active_page:
            logger.error("Sem página ativa para healing.")
            return False
            
        page = self.daemon._active_page
        
        try:
            raw_html = await page.content()
            cleaned_html = self._clean_html(raw_html)
            
            # Ler o código atual do dom_parser e dom_streamer
            with open("src/browser_automation/dom_parser.py", "r", encoding="utf-8") as f:
                parser_code = f.read()
            with open("src/browser_automation/dom_streamer.py", "r", encoding="utf-8") as f:
                streamer_code = f.read()
                
            prompt = f"""[SYSTEM HEALING PROTOCOL]
O sistema de extração de DOM falhou. O seletor CSS '{failed_selector}' para a plataforma '{platform}' não encontrou mais a mensagem.
Houve provavelmente uma atualização na interface web (DOM) do seu provedor.

Abaixo está a estrutura HTML ATUAL da página:
```html
{cleaned_html}
```

Abaixo está o código do nosso `dom_parser.py`:
```python
{parser_code}
```

E o trecho relevante de `dom_streamer.py` (onde ficam os seletores principais):
```python
{streamer_code}
```

Sua tarefa:
Analise o HTML atual e descubra a nova estrutura/classes onde as mensagens do assistente são renderizadas.
Se for necessário alterar o seletor principal, use <<<FILE_PATCH:src/browser_automation/dom_streamer.py>>>.
Se for necessário alterar a lógica de conversão, use <<<FILE_PATCH:src/browser_automation/dom_parser.py>>>.

Exemplo de uso:
<<<FILE_PATCH:src/browser_automation/dom_streamer.py>>>
@@ -22,7 +22,7 @@
     SELECTORS = {{
-        "gpt": "div[data-message-author-role='assistant']",
+        "gpt": "div.nova-classe-do-chatgpt",
         "gemini": "message-content",
<<<END_PATCH>>>

Por favor, forneça os patches necessários AGORA para se auto-consertar. Você DEVE usar o protocolo AACP.
"""

            logger.info("Enviando prompt de Healing para a IA...")
            success = await self.feeder.send_prompt(prompt, platform)
            if not success:
                logger.error("Falha ao enviar o prompt de Healing.")
                return False

            # Aguardar a resposta via innerText bruto, já que o parser normal está quebrado
            logger.info("Aguardando resposta do patch (AACP bruto)...")
            start_time = asyncio.get_event_loop().time()
            timeout = 90.0 # 90 segundos de timeout para gerar o patch
            
            patch_applied = False
            last_text = ""
            
            while (asyncio.get_event_loop().time() - start_time) < timeout:
                await asyncio.sleep(2.0)
                
                # Pegar todo o texto visível da página
                inner_text = await page.evaluate("document.body.innerText")
                
                if "<<<END_PATCH>>>" in inner_text or "<<<END_FILE>>>" in inner_text:
                    # Encontrou a resposta completa!
                    logger.info("Patch recebido! Extraindo e aplicando...")
                    
                    # Vamos pegar a difenreça (o final do inner_text onde a nova msg apareceu)
                    # AACPParser consegue varrer texto sujo
                    actions = AACPParser.parse(inner_text)
                    for action in actions:
                        if action.action_type.value in ["FILE_PATCH", "FILE_REPLACE"]:
                            logger.info(f"Aplicando {action.action_type.value} em {action.path}...")
                            FileExecutor.execute(action, workspace_override=None)
                            patch_applied = True
                    
                    if patch_applied:
                        logger.info("Self-Healing concluído com sucesso!")
                        return True
                        
            logger.error("Timeout aguardando o patch de cura.")
            return False

        except Exception as e:
            logger.error(f"Erro crítico durante o Self-Healing: {e}")
            return False
