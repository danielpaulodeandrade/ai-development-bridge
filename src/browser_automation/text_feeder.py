import logging
import asyncio
from playwright.async_api import Page
from .browser_daemon import BrowserDaemon

logger = logging.getLogger(__name__)

class TextFeeder:
    """
    Motor Textual responsável por particionar arquivos locais (Text Chunking) 
    e injetar as partes sequencialmente em inputs de chat (Textarea/ContentEditable).
    """
    
    SELECTORS = {
        "gemini": {
            "input": ".ql-editor, rich-textarea", 
            "submit": "button[aria-label='Send message'], .send-button"
        },
        "chatgpt": {
            "input": "#prompt-textarea", 
            "submit": "button[data-testid='send-button']"
        },
        "claude": {
            "input": "div[contenteditable='true']", 
            "submit": "button[aria-label='Send Message']"
        },
        "deepseek": {
            "input": "#chat-input", 
            "submit": "button.send"
        }
    }

    def __init__(self, daemon: BrowserDaemon, max_chunk_size: int = 8000):
        self.daemon = daemon
        self.max_chunk_size = max_chunk_size

    def _chunk_text(self, text: str) -> list[str]:
        """Divide o texto respeitando quebras de linha."""
        chunks = []
        current_chunk = ""
        
        for line in text.split('\n'):
            if len(line) > self.max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                for i in range(0, len(line), self.max_chunk_size):
                    chunks.append(line[i:i+self.max_chunk_size])
                continue

            if len(current_chunk) + len(line) + 1 > self.max_chunk_size:
                chunks.append(current_chunk)
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"
                
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    async def _wait_for_ai_ready(self, page: Page):
        """Estratégia: Espera a rede ociosa + Delay de UI."""
        logger.info("Aguardando IA processar a parte anterior...")
        try:
            await page.wait_for_load_state("networkidle", timeout=8000)
            await asyncio.sleep(1.5)
        except Exception:
            # Se der timeout, fallback para sleep bruto
            await asyncio.sleep(4)

    async def feed(self, file_content: str, filename: str, platform: str = "gemini") -> bool:
        if not self.daemon._active_page:
            raise RuntimeError("BrowserDaemon não possui uma página ativa.")
        
        page = self.daemon._active_page
        selectors = self.SELECTORS.get(platform.lower())
        if not selectors:
            logger.warning(f"Plataforma '{platform}' não mapeada.")
            return False
            
        chunks = self._chunk_text(file_content)
        total = len(chunks)

        for idx, chunk in enumerate(chunks, 1):
            if total > 1:
                if idx == 1:
                    prompt = f"Vou enviar o arquivo '{filename}' em {total} partes. Responda APENAS 'Recebido {idx}/{total}' e aguarde.\n\n{chunk}"
                elif idx == total:
                    prompt = f"Última parte {idx}/{total} de '{filename}'.\n\n{chunk}"
                else:
                    prompt = f"Parte {idx}/{total} de '{filename}'. Responda APENAS 'Recebido {idx}/{total}'.\n\n{chunk}"
            else:
                prompt = f"Conteúdo de '{filename}':\n\n{chunk}"

            try:
                # Usar evaluate para injetar o texto no textarea costuma ser mais rápido/robusto
                input_el = page.locator(selectors["input"]).first
                await input_el.wait_for(state="visible", timeout=10000)
                await input_el.fill(prompt)
                
                btn = page.locator(selectors["submit"]).first
                await btn.wait_for(state="visible", timeout=5000)
                await btn.click()
                
                if idx < total:
                    await self._wait_for_ai_ready(page)
                    
            except Exception as e:
                logger.error(f"Erro no envio da parte {idx}: {e}")
                return False
                
        return True

    async def send_prompt(self, prompt: str, platform: str = "gemini") -> bool:
        """Envia um prompt direto sem tratá-lo como arquivo particionado."""
        if not self.daemon._active_page:
            raise RuntimeError("BrowserDaemon não possui uma página ativa.")
        
        page = self.daemon._active_page
        selectors = self.SELECTORS.get(platform.lower())
        if not selectors:
            logger.warning(f"Plataforma '{platform}' não mapeada.")
            return False

        try:
            input_el = page.locator(selectors["input"]).first
            await input_el.wait_for(state="visible", timeout=10000)
            await input_el.fill(prompt)
            
            btn = page.locator(selectors["submit"]).first
            await btn.wait_for(state="visible", timeout=5000)
            await btn.click()
            
            await self._wait_for_ai_ready(page)
            return True
        except Exception as e:
            logger.error(f"Erro no envio do prompt: {e}")
            return False
