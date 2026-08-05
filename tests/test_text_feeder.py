import pytest
import asyncio
from src.browser_automation.text_feeder import TextFeeder

def test_chunk_text():
    """Testa se o TextFeeder divide os textos corretamente respeitando limites."""
    feeder = TextFeeder(daemon=None, max_chunk_size=20)
    
    # Texto com 3 linhas curtas
    text = "Line 1\nLine 2\nLine 3"
    chunks = feeder._chunk_text(text)
    
    assert len(chunks) > 0
    # A união dos chunks não deve perder informação
    joined = "".join(chunks).strip()
    assert joined.replace('\n', '') == text.replace('\n', '')

def test_chunk_text_long_line():
    """Testa divisão de uma linha maior que o max_chunk_size."""
    feeder = TextFeeder(daemon=None, max_chunk_size=10)
    text = "ThisIsAVeryLongLineWithoutBreaks"
    chunks = feeder._chunk_text(text)
    
    assert len(chunks) == 4
    assert chunks[0] == "ThisIsAVer"
    assert chunks[1] == "yLongLineW"
    
    # Restaura pra garantir que nada foi perdido
    assert "".join(chunks) == text
