import os
from src.workspace_core.size_controller import ContextChunk
from src.workspace_core.exporter import MarkdownExporter

def test_markdown_exporter(tmp_path):
    output_dir = tmp_path / "context"
    exporter = MarkdownExporter(output_dir=str(output_dir))
    
    chunks = [
        ContextChunk(index=1, total_chunks=2, text_content="part 1 content"),
        ContextChunk(index=2, total_chunks=2, text_content="part 2 content")
    ]
    
    saved = exporter.export("M1-024", chunks)
    
    assert len(saved) == 2
    
    p1 = output_dir / "M1-024" / "M1-024-part1.md"
    p2 = output_dir / "M1-024" / "M1-024-part2.md"
    
    assert p1.exists()
    assert p2.exists()
    assert p1.read_text(encoding="utf-8") == "part 1 content"
    assert p2.read_text(encoding="utf-8") == "part 2 content"
