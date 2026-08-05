import os
import logging
from playwright.async_api import async_playwright, BrowserContext, Page, Playwright

logger = logging.getLogger(__name__)

class BrowserDaemon:
    """
    Singleton que mantém a instância do navegador viva em background.
    Gerencia a sessão (cookies, perfil persistente) para evitar logins recorrentes.
    """
    _instance = None

    def __init__(self, headless: bool = False, profile_dir_name: str = ".browser_profile"):
        self.headless = headless
        self._playwright: Playwright | None = None
        self._context: BrowserContext | None = None
        self._active_page: Page | None = None
        
        # Profile directory for persistent session
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.user_data_dir = os.path.join(base_dir, profile_dir_name)
        
    @classmethod
    async def get_instance(cls, headless: bool = False) -> 'BrowserDaemon':
        """Retorna a instância singleton do BrowserDaemon, iniciando-o se necessário."""
        if cls._instance is None:
            cls._instance = cls(headless=headless)
            await cls._instance.start()
        return cls._instance

    async def start(self):
        """Inicia o Playwright com um contexto persistente (preserva login/cookies)."""
        if self._context:
            return

        logger.info(f"Iniciando BrowserDaemon com perfil persistente em: {self.user_data_dir}")
        self._playwright = await async_playwright().start()
        
        # Lança Chromium ignorando detecções básicas de automação
        self._context = await self._playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ],
            no_viewport=True,  # Permite que a janela redimensione livremente
            permissions=["clipboard-read", "clipboard-write"] # Crucial para M4-002 extrair markdown nativo
        )
        
        pages = self._context.pages
        if pages:
            self._active_page = pages[0]
        else:
            self._active_page = await self._context.new_page()

    async def navigate(self, url: str) -> Page:
        """
        Navega para a URL desejada na aba ativa. 
        Se já estiver na URL (ou subcaminho dela), retorna instantaneamente.
        """
        if not self._active_page:
            raise RuntimeError("BrowserDaemon não foi iniciado corretamente. Nenhuma aba ativa encontrada.")

        current_url = self._active_page.url
        if not current_url.startswith(url):
            logger.info(f"Navegando para: {url}")
            await self._active_page.goto(url, wait_until="domcontentloaded")
        else:
            logger.debug(f"Aba já se encontra no domínio/url {url}.")
            
        return self._active_page

    async def stop(self):
        """Encerra o Daemon e fecha o navegador, salvando o perfil."""
        if self._context:
            await self._context.close()
            self._context = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        
        BrowserDaemon._instance = None
        logger.info("BrowserDaemon finalizado.")
