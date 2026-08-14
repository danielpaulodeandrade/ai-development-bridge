import os
import shutil
from src.agent.models import FileAction, ActionType
from src.config import Settings

class FileExecutor:
    """Executa ações de arquivo lidas pelo AACPParser com proteções de segurança"""

    @staticmethod
    def _sanitize_path(relative_path: str, dynamic_workspace: str = None) -> str:
        """
        Garante que o caminho do arquivo não escape do diretório do workspace 
        (Prevenção de Path Traversal).
        """
        base = dynamic_workspace if dynamic_workspace else Settings().get_workspace_dir()
        base_dir = os.path.abspath(base)
        
        # Remove barras iniciais para garantir que os.path.join funcione corretamente
        clean_relative = relative_path.lstrip("\\/")
        
        target_path = os.path.abspath(os.path.join(base_dir, clean_relative))
        
        if not target_path.startswith(base_dir):
            raise PermissionError(f"Acesso negado: Tentativa de manipulação fora do Workspace. Caminho: {target_path}")
            
        return target_path

    @classmethod
    def execute(cls, action: FileAction, dynamic_workspace: str = None) -> str:
        """
        Recebe uma FileAction e a executa com segurança, retornando uma mensagem de sucesso
        """
        try:
            target_path = cls._sanitize_path(action.path, dynamic_workspace)
            
            if action.action_type == ActionType.FILE_CREATE:
                return cls._create_file(target_path, action.content)
            
            elif action.action_type == ActionType.FILE_REPLACE:
                return cls._replace_file(target_path, action.content)
                
            elif action.action_type == ActionType.DELETE_FILE:
                return cls._delete_file(target_path)
                
            elif action.action_type == ActionType.MOVE_FILE:
                destination = cls._sanitize_path(action.destination_path, dynamic_workspace)
                return cls._move_file(target_path, destination)
                
            elif action.action_type == ActionType.MKDIR:
                return cls._make_dir(target_path)
                
            else:
                raise ValueError(f"Ação não suportada pelo FileExecutor: {action.action_type}")
                
        except Exception as e:
            return f"❌ Erro ao executar {action.action_type.value} em {action.path}: {str(e)}"

    @staticmethod
    def _create_file(path: str, content: str) -> str:
        if os.path.exists(path):
            raise FileExistsError("O arquivo já existe. Use FILE_REPLACE para sobrescrever.")
            
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content if content else "")
            
        return f"✅ Arquivo criado: {path}"

    @staticmethod
    def _replace_file(path: str, content: str) -> str:
        # Se existir, criar backup
        if os.path.exists(path):
            backup_path = path + ".bak"
            shutil.copy2(path, backup_path)
        else:
            # Se não existir, criar diretórios pais (resiliência solicitada)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
        with open(path, "w", encoding="utf-8") as f:
            f.write(content if content else "")
            
        if os.path.exists(path + ".bak"):
            return f"✅ Arquivo substituído (backup salvo em .bak): {path}"
        return f"✅ Arquivo criado automaticamente via substituição: {path}"

    @staticmethod
    def _delete_file(path: str) -> str:
        if not os.path.exists(path):
            return f"⚠️ Arquivo ignorado (não existia): {path}"
            
        os.remove(path)
        return f"✅ Arquivo removido: {path}"

    @staticmethod
    def _move_file(src_path: str, dst_path: str) -> str:
        if not os.path.exists(src_path):
            raise FileNotFoundError("O arquivo de origem não existe.")
            
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.move(src_path, dst_path)
        return f"✅ Arquivo movido: de {src_path} para {dst_path}"

    @staticmethod
    def _make_dir(path: str) -> str:
        if os.path.exists(path):
            return f"⚠️ Diretório já existe: {path}"
            
        os.makedirs(path, exist_ok=True)
        return f"✅ Diretório criado: {path}"
