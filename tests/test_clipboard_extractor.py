import pytest
import asyncio
import os
from src.browser_automation.browser_daemon import BrowserDaemon
from src.browser_automation.clipboard_extractor import ClipboardExtractor

def test_clipboard_extractor_gemini():
    """Testa se o ClipboardExtractor consegue ler o markdown do botao Copiar do HTML mock"""
    async def run_test():
        daemon = await BrowserDaemon.get_instance(headless=True)
        
        # O playwright precisa servir o HTML local ou carregar via file://
        dummy_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "dummy_chat.html"))
        # Usa file URI scheme no windows precisa de /// e barras normais
        file_uri = f"file:///{dummy_path.replace(chr(92), '/')}" 
        
        await daemon.navigate(file_uri)
        
        extractor = ClipboardExtractor(daemon)
        markdown = await extractor.extract_last_response(platform="gemini")
        
        assert markdown is not None
        assert "Markdown puro!" in markdown
        
        await daemon.stop()
        
    asyncio.run(run_test())
