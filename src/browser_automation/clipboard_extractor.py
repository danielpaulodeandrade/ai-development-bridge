import logging
import asyncio
from typing import Optional
from playwright.async_api import Page
from .browser_daemon import BrowserDaemon

logger = logging.getLogger(__name__)

class ClipboardExtractor:
    """
    Responsável por encontrar botões de cópia nativos na UI (Gemini, ChatGPT)
    e ler o conteúdo (Markdown) perfeitamente gerado pela plataforma direto do Clipboard.
    """
    
    # Mapeamento de seletores conhecidos de "Copiar" por plataforma
    SELECTORS = {
        # Gemini usa material icons com data-mat-icon-name="copy" ou aria-label="Copy"
        "gemini": [
            "button[aria-label='Copy']",
            "mat-icon[data-mat-icon-name='copy']",
            ".buttons-container-v2 button"
        ],
        "chatgpt": [
            "button[data-testid='copy-turn-action-button']"
        ],
        "claude": [
            "button[aria-label='Copiar']",
            "button[aria-label='Copy']"
        ],
        "deepseek": [
            ".ds-button--iconLabelTertiary:has(svg path[d^='M6.14929'])"
        ],
        "meta": [
            "button[aria-label='Copiar respuesta']"
        ],
        "deepai": [
            "button.copytextButton",
            "button[data-tooltip='Copy']"
        ],
        "copilot": [
            "button[data-testid='copy-ai-message-button']",
            "button[data-testid='copy-table-button']"
        ],
        "poe": [
            "button[aria-label='Copiar mensaje']"
        ],
        "perplexity": [
            "button[aria-label='Copiar']"
        ]
    }

    def __init__(self, daemon: BrowserDaemon):
        self.daemon = daemon

    async def get_page(self) -> Page:
        if not self.daemon._active_page:
            raise RuntimeError("BrowserDaemon não possui uma página ativa.")
        return self.daemon._active_page

    async def extract_last_response(self, prompt: str, platform: str = "gemini", timeout_ms: int = 60000) -> Optional[str]:
        """
        Localiza o ÚLTIMO botão de cópia na tela (que geralmente pertence à última resposta da IA),
        clica nele e lê o conteúdo da área de transferência (Clipboard).
        Fica em polling aguardando o botão aparecer (aguardando o fim da geração da IA).
        Ignora cópias do próprio prompt do usuário.
        """
        page = await self.get_page()
        
        selectors = self.SELECTORS.get(platform.lower())
        if not selectors:
            logger.warning(f"Plataforma '{platform}' não mapeada no ClipboardExtractor.")
            return None

        # Limpa o clipboard (escrevemos string vazia no navegador)
        await page.evaluate("navigator.clipboard.writeText('')")

        logger.info(f"Aguardando geração da IA (timeout de {timeout_ms/1000}s)... procurando botões de cópia.")
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < (timeout_ms / 1000.0):
            for selector in selectors:
                try:
                    elements = await page.locator(selector).all()
                    if elements:
                        # Pegamos o ÚLTIMO botão que corresponde ao seletor (garantido de ser o de cópia pelo seletor preciso)
                        last_button = elements[-1]
                        
                        if await last_button.is_visible():
                            # Clica silenciosamente
                            await last_button.scroll_into_view_if_needed()
                            await last_button.click(timeout=3000)
                            await asyncio.sleep(0.5) 
                            
                            clipboard_text = await page.evaluate("navigator.clipboard.readText()")
                            
                            # Adicionando uma verificação extra para garantir que não vazamos links públicos acidentalmente
                            if clipboard_text and clipboard_text.strip() != prompt.strip() and not clipboard_text.strip().startswith("https://chat.deepseek.com/share/"):
                                logger.info(f"Conteúdo extraído com sucesso via seletor: {selector}")
                                return clipboard_text
                            else:
                                # Limpa o clipboard se copiou a pergunta do usuário ou se o clique foi em outro botão (ex: curtir)
                                await page.evaluate("navigator.clipboard.writeText('')")
                except Exception:
                    continue
            
            await asyncio.sleep(2) # Polling interval
                
        logger.warning(f"Timeout atingido. Tentando Self-Healing para: {platform}...")
        
        from .adaptive_recovery import AdaptiveRecovery
        recovery = AdaptiveRecovery()
        
        # Tenta cache
        cached_sel = recovery.get_cached_selector(platform, "copy_button")
        if cached_sel:
            try:
                btn = page.locator(cached_sel).last
                await btn.scroll_into_view_if_needed()
                await btn.click(timeout=3000)
                await asyncio.sleep(0.5)
                return await page.evaluate("navigator.clipboard.readText()")
            except Exception:
                pass
        
        # Tenta LLM
        new_sel = await recovery.recover(page, platform, "copy_button")
        if new_sel:
            try:
                btn = page.locator(new_sel).last
                await btn.scroll_into_view_if_needed()
                await btn.click(timeout=3000)
                await asyncio.sleep(0.5)
                return await page.evaluate("navigator.clipboard.readText()")
            except Exception:
                pass
                
        logger.error("Self-Healing falhou. Botão de cópia não foi encontrado.")
        return None
