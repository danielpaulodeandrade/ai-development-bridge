import sys
import importlib
import logging

logger = logging.getLogger(__name__)

class HotReloader:
    @staticmethod
    def reload_browser_automation():
        """
        Recarrega os módulos críticos de automação do browser para 
        aplicar as mudanças feitas via self-healing (AACP Patch).
        """
        try:
            logger.info("Hot-reloading módulos do parser e streamer...")
            
            # Recarrega o parser primeiro
            if 'src.browser_automation.dom_parser' in sys.modules:
                import src.browser_automation.dom_parser as dp
                importlib.reload(dp)
                
            # Recarrega o streamer
            if 'src.browser_automation.dom_streamer' in sys.modules:
                import src.browser_automation.dom_streamer as ds
                importlib.reload(ds)
                
            logger.info("Módulos recarregados com sucesso.")
            return True
        except Exception as e:
            logger.error(f"Erro no hot-reload: {e}")
            return False
