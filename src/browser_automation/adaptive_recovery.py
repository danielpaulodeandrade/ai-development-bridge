import json
import logging
import os
from typing import Optional
from playwright.async_api import Page
from src.provider_system import ProviderRegistry, ProviderMessage

logger = logging.getLogger(__name__)

class AdaptiveRecovery:
    """
    Self-Healing mechanism. Usa LLMs para recuperar seletores quebrados na interface.
    """
    CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".browser_profile", "selectors_cache.json")

    def __init__(self):
        self.fallback = ProviderRegistry.get_provider("fallback")
        if not self.fallback:
            raise RuntimeError("FallbackProvider não configurado no ProviderRegistry. Certifique-se de importar e registrar o provider.")
        
    def _load_cache(self) -> dict:
        if os.path.exists(self.CACHE_FILE):
            try:
                with open(self.CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self, cache: dict):
        os.makedirs(os.path.dirname(self.CACHE_FILE), exist_ok=True)
        with open(self.CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=4)

    def get_cached_selector(self, platform: str, target_type: str) -> Optional[str]:
        cache = self._load_cache()
        return cache.get(platform, {}).get(target_type)

    def update_cache(self, platform: str, target_type: str, new_selector: str):
        cache = self._load_cache()
        if platform not in cache:
            cache[platform] = {}
        cache[platform][target_type] = new_selector
        self._save_cache(cache)
        logger.info(f"Cache de seletores atualizado: {platform}.{target_type} = {new_selector}")

    async def recover(self, page: Page, platform: str, target_type: str) -> Optional[str]:
        """
        Gera snapshot da árvore de acessibilidade, envia para LLM e retorna o novo seletor testado.
        """
        logger.warning(f"Iniciando AdaptiveRecovery (Self-Healing) para {platform} ({target_type})...")
        
        try:
            # Pega árvore de acessibilidade para poupar tokens drásticamente
            snapshot = await page.aria_snapshot()
            tree_str = snapshot[:10000] # Proteção de limite de contexto do Groq
            
            prompt = f"""Você é um bot autônomo de recuperação de interface (Self-Healing). 
A interface do {platform} atualizou e nosso automador Playwright quebrou.
O elemento alvo que busco encontrar na tela é: '{target_type}'.

Dicas:
- Se for botão de cópia: normalmente possui aria-label como 'Copy', 'Copiar' ou um icone svg.
- Se for chat input: geralmente é um textarea, ou div com contenteditable=true e placeholder de mensagem.
- Se for botão de envio: normalmente um botão próximo ao input com aria-label de 'Send' ou svg de avião de papel.

Baseado estritamente na árvore de acessibilidade abaixo, retorne APENAS E EXCLUSIVAMENTE uma string que seja um seletor CSS válido e direto para capturar o alvo na tela. Não escreva código markdown ou explicações, apenas o seletor.

Accessibility Tree:
{tree_str}"""
            
            msg = ProviderMessage(role="user", content=prompt)
            resp = self.fallback.send_prompt([msg])
            
            # Limpa resposta do LLM caso venha com formatação markdown acidental
            new_selector = resp.content.strip().replace("```css", "").replace("```html", "").replace("```", "").strip()
            
            logger.info(f"O LLM Sugeriu o novo seletor: '{new_selector}'")
            
            if not new_selector:
                return None
                
            # Testa o seletor na página em tempo real (Self-Healing)
            count = await page.locator(new_selector).count()
            if count > 0:
                logger.info(f"Sucesso! O seletor '{new_selector}' encontrou {count} elemento(s). Salvando no cache permanente.")
                self.update_cache(platform, target_type, new_selector)
                return new_selector
            else:
                logger.error(f"O seletor sugerido '{new_selector}' não encontrou nenhum elemento na tela. O Self-Healing falhou.")
                return None
                
        except Exception as e:
            logger.error(f"Falha fatal no AdaptiveRecovery: {e}")
            return None
