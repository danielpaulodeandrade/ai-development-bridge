import os
from datetime import datetime
from src.workspace_core.scanner import FileMeta
from src.workspace_core.size_controller import ContextSizeController, SizeRules

def test_size_controller_chunking(tmp_path):
    f1 = tmp_path / "a.txt"
    f1.write_text("1234567890\n" * 100) # 1100 chars
    f2 = tmp_path / "b.txt"
    f2.write_text("abcdefghij\n" * 100) # 1100 chars
    
    files = [
        FileMeta(path="a.txt", size_bytes=1100, extension=".txt", last_modified=datetime.now()),
        FileMeta(path="b.txt", size_bytes=1100, extension=".txt", last_modified=datetime.now())
    ]
    
    # Total characters vai girar em torno de 2200 + separadores
    rules = SizeRules(max_chars_per_chunk=1000)
    controller = ContextSizeController(rules, root_path=str(tmp_path))
    
    chunks = controller.chunk_files(files)
    
    assert len(chunks) >= 3
    assert chunks[0].index == 1
    assert chunks[0].total_chunks == len(chunks)
    assert "[Parte 1" in chunks[0].text_content
    assert chunks[-1].index == len(chunks)
    assert "Fim do contexto" in chunks[-1].text_content

def test_size_controller_no_chunking(tmp_path):
    f1 = tmp_path / "a.txt"
    f1.write_text("small")
    
    files = [
        FileMeta(path="a.txt", size_bytes=5, extension=".txt", last_modified=datetime.now()),
    ]
    
    rules = SizeRules(max_chars_per_chunk=1000)
    controller = ContextSizeController(rules, root_path=str(tmp_path))
    
    chunks = controller.chunk_files(files)
    
    assert len(chunks) == 1
    assert chunks[0].index == 1
    assert chunks[0].total_chunks == 1
    assert "[Parte 1" not in chunks[0].text_content
