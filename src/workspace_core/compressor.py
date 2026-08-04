import ast
import re

class CodeCompressor:
    """Responsável por reduzir o tamanho de códigos removendo comentários e docstrings."""
    
    @staticmethod
    def compress_python(source_code: str) -> str:
        """Comprime código Python removendo docstrings, comentários e linhas em branco extras."""
        try:
            # Parseia para AST
            parsed = ast.parse(source_code)
        except SyntaxError:
            # Se for um trecho de código inválido, cai pro minificador básico
            return CodeCompressor._basic_minify(source_code)
            
        # Remover docstrings
        for node in ast.walk(parsed):
            if not isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef, ast.Module)):
                continue
            if not node.body:
                continue
            first_node = node.body[0]
            if isinstance(first_node, ast.Expr) and isinstance(first_node.value, ast.Constant) and isinstance(first_node.value.value, str):
                node.body.pop(0)
                
        # Gerar o código novamente. 
        # ast.unparse automaticamente ignora todos os comentários com # que não fazem parte do AST!
        try:
            compressed = ast.unparse(parsed)
            return CodeCompressor._basic_minify(compressed)
        except Exception:
            return CodeCompressor._basic_minify(source_code)
            
    @staticmethod
    def _basic_minify(text: str) -> str:
        """Remove comentários que começam a linha e linhas em branco."""
        lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith('#'):
                continue
            lines.append(line)
        
        return "\n".join(lines)
