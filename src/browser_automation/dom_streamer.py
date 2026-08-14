import asyncio
import logging
from typing import AsyncGenerator
from playwright.async_api import Page
from .browser_daemon import BrowserDaemon
from .dom_parser import (
    ChatGPTDOMParser, GeminiDOMParser, ClaudeDOMParser,
    DeepseekDOMParser, QwenDOMParser, KimiDOMParser,
    DeepAIDOMParser, GrokDOMParser, ChatXDOMParser
)
from src.agent.hot_reloader import HotReloader

logger = logging.getLogger(__name__)

class DOMStreamer:
    """
    Componente do V2 Streaming Engine.
    Responsável por capturar o DOM do navegador em tempo real enquanto a IA gera a resposta
    e converter incrementalmente para Markdown (produzindo deltas).
    """

    # Seletores CSS para encontrar o container da mensagem gerada pela IA
    SELECTORS = {
        "gpt": "div[data-message-author-role='assistant'], [data-message-role='assistant']",
        "chatgpt": "div[data-message-author-role='assistant'], [data-message-role='assistant']",
        "gemini": "message-content",
        "claude": "div.font-claude-response",
        "deepseek": "div.ds-message", # Deepseek's assistant message container
        "qwen": "div.qwen-chat-message-assistant",
        "kimi": "div.chat-content-item-assistant",
        "deepai": "span.hiddenTextContainer",
        "grok": "div.message-bubble", # We'll need to grab the last one and let parser decide, but Grok last message is usually assistant
        "chatx": "div.system_write"
    }

    def __init__(self, daemon: BrowserDaemon):
        self.daemon = daemon

    def _get_parser(self, platform: str):
        p = platform.lower()
        if p == 'gemini': return GeminiDOMParser()
        elif p == 'claude': return ClaudeDOMParser()
        elif p == 'deepseek': return DeepseekDOMParser()
        elif p == 'qwen': return QwenDOMParser()
        elif p == 'kimi': return KimiDOMParser()
        elif p == 'deepai': return DeepAIDOMParser()
        elif p == 'grok': return GrokDOMParser()
        elif p == 'chatx': return ChatXDOMParser()
        else: return ChatGPTDOMParser()

    async def get_page(self) -> Page:
        if not self.daemon._active_page:
            raise RuntimeError("BrowserDaemon não possui uma página ativa.")
        return self.daemon._active_page

    async def stream_response(self, platform: str, timeout_ms: int = 60000, poll_interval_s: float = 0.2) -> AsyncGenerator[str, None]:
        """
        Yields Markdown deltas (os novos caracteres gerados pela IA).
        Fica em polling lendo o DOM até perceber que a IA terminou de gerar.
        """
        page = await self.get_page()
        selector = self.SELECTORS.get(platform.lower())
        
        if not selector:
            logger.warning(f"Plataforma '{platform}' não mapeada no DOMStreamer. Fallback para clipboard.")
            yield ""
            return

        parser = self._get_parser(platform)
        
        start_time = asyncio.get_event_loop().time()
        last_markdown = ""
        stable_count = 0
        
        # Espera inicial para a IA começar a responder
        await asyncio.sleep(1.0)
        
        while (asyncio.get_event_loop().time() - start_time) < (timeout_ms / 1000.0):
            try:
                # Pega o outerHTML do último bloco de resposta da IA
                loc = page.locator(selector).last
                
                # Se não existir ainda, apenas continua tentando
                if await loc.count() == 0:
                    await asyncio.sleep(poll_interval_s)
                    continue

                html_content = await loc.evaluate("el => el.outerHTML")
                
                # Converte o HTML atual para Markdown
                current_markdown = parser.parse_html_to_markdown(html_content)
                
                # Tratamento para parser que retornam blocos com separadores ---\n\n
                current_markdown = current_markdown.split("\n\n---\n\n")[-1].strip()
                
                if current_markdown != last_markdown:
                    # Verifica o que mudou (Delta)
                    if current_markdown.startswith(last_markdown):
                        delta = current_markdown[len(last_markdown):]
                    else:
                        # Se o texto mudou no meio (ex: correção de formatação do DOM), re-enviamos tudo (simplificação)
                        # Na prática, o SSE do OpenAI concatena, então precisamos do delta real.
                        # Uma técnica segura é encontrar o prefixo comum máximo se o markdown não for estritamente aditivo.
                        import os
                        common_prefix = os.path.commonprefix([last_markdown, current_markdown])
                        # Por simplicidade e evitar quebrar UI, se divergir muito assumimos que é aditivo baseado no common_prefix
                        # Como é um streaming aditivo na maioria das vezes, `startswith` funciona em 99% dos casos.
                        if len(common_prefix) > 0:
                            delta = current_markdown[len(common_prefix):]
                        else:
                            delta = current_markdown
                            
                    if delta:
                        yield delta
                        
                    last_markdown = current_markdown
                    stable_count = 0
                else:
                    stable_count += 1
                    
                # Condição de parada simplificada: 15 ticks consecutivos (3 segundos) sem mudança = terminou
                # O ideal seria verificar o botão de 'stop generating', mas a estabilidade funciona universalmente.
                if stable_count >= 15:
                    break

            except Exception as e:
                # O elemento pode ter sumido temporariamente se o DOM foi re-renderizado
                logger.debug(f"DOMStreamer error: {e}")
                
            await asyncio.sleep(poll_interval_s)
            
        if stable_count < 15:
            logger.warning(f"DOMStreamer: Timeout de {timeout_ms}ms atingido antes da estabilização.")

        if not last_markdown:
            logger.error(f"Extração falhou completamente para {platform}. Disparando Self-Healing...")
            from .self_healing import SelfHealingEngine
            healer = SelfHealingEngine(self.daemon)
            healed = await healer.initiate_healing(platform, selector)
            if healed:
                HotReloader.reload_browser_automation()
                logger.info("Self-healing concluído. Sugere-se tentar o prompt novamente.")
                yield "\n\n> 🛠️ **Bridge Self-Healing System:** Detectei uma mudança na interface do site, mas consegui me consertar! Por favor, mande sua mensagem novamente."
            else:
                yield "\n\n> ❌ **Bridge Self-Healing System:** Falhei ao extrair a resposta e não consegui me consertar. Verifique os logs."
