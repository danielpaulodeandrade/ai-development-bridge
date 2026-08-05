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
            "button[aria-label='Copiar']"
        ],
        "deepseek": [
            ".ds-button--iconLabelTertiary"
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

    async def extract_last_response(self, platform: str = "gemini") -> Optional[str]:
        """
        Localiza o ÚLTIMO botão de cópia na tela (que geralmente pertence à última resposta da IA),
        clica nele e lê o conteúdo da área de transferência (Clipboard).
        """
        page = await self.get_page()
        
        selectors = self.SELECTORS.get(platform.lower())
        if not selectors:
            logger.warning(f"Plataforma '{platform}' não mapeada no ClipboardExtractor.")
            return None

        # Limpa o clipboard (escrevemos string vazia no navegador)
        await page.evaluate("navigator.clipboard.writeText('')")

        clicked = False
        for selector in selectors:
            try:
                # O timeout precisa ser curto pois tentaremos o próximo seletor
                elements = await page.locator(selector).all()
                if elements:
                    # Sempre pegamos o ÚLTIMO botão de cópia encontrado na tela
                    last_button = elements[-1]
                    logger.info(f"Clicando no botão de copiar via seletor: {selector}")
                    # Scroll into view and click
                    await last_button.scroll_into_view_if_needed()
                    await last_button.click(timeout=3000)
                    
                    # Aguarda a ação do site escrever no clipboard (as vezes tem animação)
                    await asyncio.sleep(0.5) 
                    
                    clicked = True
                    break
            except Exception as e:
                logger.debug(f"Falha ao clicar no seletor '{selector}': {e}")
                continue
                
        if not clicked:
            logger.warning(f"Não foi possível encontrar nenhum botão de cópia na lista estática para: {platform}. Tentando Self-Healing...")
            
            from .adaptive_recovery import AdaptiveRecovery
            recovery = AdaptiveRecovery()
            
            # Tenta primeiro usar o que já foi curado e salvo no cache
            cached_sel = recovery.get_cached_selector(platform, "copy_button")
            if cached_sel:
                try:
                    logger.info(f"Tentando seletor do cache: {cached_sel}")
                    btn = page.locator(cached_sel).last
                    await btn.scroll_into_view_if_needed()
                    await btn.click(timeout=3000)
                    await asyncio.sleep(0.5)
                    clicked = True
                except Exception as e:
                    logger.debug(f"Cache falhou, partindo para o LLM. Erro: {e}")
            
            # Se o cache falhar, invoca o LLM local para descobrir o novo seletor
            if not clicked:
                new_sel = await recovery.recover(page, platform, "copy_button")
                if new_sel:
                    try:
                        logger.info("Executando clique com o novo seletor curado pelo LLM.")
                        btn = page.locator(new_sel).last
                        await btn.scroll_into_view_if_needed()
                        await btn.click(timeout=3000)
                        await asyncio.sleep(0.5)
                        clicked = True
                    except Exception as e:
                        logger.error(f"Mesmo com o LLM, o clique falhou: {e}")
                        
            if not clicked:
                logger.error("Self-Healing falhou. Botão de cópia não foi encontrado.")
                return None

        # Lê o conteúdo do clipboard usando a API do navegador nativa injetada via evaluate
        try:
            clipboard_text = await page.evaluate("navigator.clipboard.readText()")
            logger.info("Conteúdo extraído com sucesso do Clipboard via Playwright!")
            return clipboard_text
        except Exception as e:
            logger.error(f"Erro ao ler navigator.clipboard (Verifique permissões do BrowserDaemon): {e}")
            return None
