from src.workspace_core.compressor import CodeCompressor

def test_compress_python():
    source = '''
"""
Module docstring
"""
import os

class MyClass:
    """Class docstring"""
    
    def my_method(self):
        """Method docstring"""
        # This is a comment
        print("hello") # inline comment
        
        
        print("world")
'''

    compressed = CodeCompressor.compress_python(source)
    
    # Docstrings should be gone
    assert "Module docstring" not in compressed
    assert "Class docstring" not in compressed
    assert "Method docstring" not in compressed
    
    # Comments should be gone
    assert "This is a comment" not in compressed
    assert "inline comment" not in compressed
    
    # Should still contain the code
    assert "import os" in compressed
    assert "class MyClass" in compressed
    assert "def my_method" in compressed
    assert "print('hello')" in compressed

def test_compress_python_fallback():
    # Invalid python code should fallback to basic minify
    source = '''
    def broken(
    # comment
    pass
    '''
    compressed = CodeCompressor.compress_python(source)
    assert "# comment" not in compressed
    assert "def broken(" in compressed
