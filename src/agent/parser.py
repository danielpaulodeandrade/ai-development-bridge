import re
from typing import List
from .models import AACPAction, ActionType, FileAction, RunAction

class AACPParser:
    """Parser para o Aletheia Agent Communication Protocol (AACP)"""
    
    # Regex para comandos com bloco de conteúdo multilinhas
    # Usa non-greedy (.*?) e re.DOTALL para pegar quebras de linha
    RE_FILE_CREATE = re.compile(r'(<<<FILE_CREATE:(.*?)>>>\s*(.*?)\s*<<<END_FILE>>>)', re.DOTALL)
    RE_FILE_REPLACE = re.compile(r'(<<<FILE_REPLACE:(.*?)>>>\s*(.*?)\s*<<<END_FILE>>>)', re.DOTALL)
    RE_FILE_PATCH = re.compile(r'(<<<FILE_PATCH:(.*?)>>>\s*(.*?)\s*<<<END_PATCH>>>)', re.DOTALL)
    RE_RUN = re.compile(r'(<<<RUN>>>\s*(.*?)\s*<<<END>>>)', re.DOTALL)
    
    # Regex para comandos inline (sem fechamento)
    RE_DELETE = re.compile(r'(<<<DELETE_FILE:(.*?)>>>)')
    RE_MKDIR = re.compile(r'(<<<MKDIR:(.*?)>>>)')
    RE_MOVE = re.compile(r'(<<<MOVE_FILE:(.*?)\|(.*?)>>>)')

    @classmethod
    def parse(cls, text: str) -> List[AACPAction]:
        """
        Recebe um texto (geralmente resposta da IA) e extrai todas as ações válidas.
        Blocos malformados que não dão match perfeitamente serão ignorados com segurança.
        """
        actions = []
        
        # Parse FILE_CREATE
        for match in cls.RE_FILE_CREATE.finditer(text):
            full_match = match.group(1)
            path = match.group(2).strip()
            content = match.group(3)
            actions.append(FileAction(action_type=ActionType.FILE_CREATE, original_match=full_match, path=path, content=content))
            
        # Parse FILE_REPLACE
        for match in cls.RE_FILE_REPLACE.finditer(text):
            full_match = match.group(1)
            path = match.group(2).strip()
            content = match.group(3)
            actions.append(FileAction(action_type=ActionType.FILE_REPLACE, original_match=full_match, path=path, content=content))
            
        # Parse FILE_PATCH
        for match in cls.RE_FILE_PATCH.finditer(text):
            full_match = match.group(1)
            path = match.group(2).strip()
            content = match.group(3)
            actions.append(FileAction(action_type=ActionType.FILE_PATCH, original_match=full_match, path=path, content=content))
            
        # Parse RUN
        for match in cls.RE_RUN.finditer(text):
            full_match = match.group(1)
            command = match.group(2).strip()
            actions.append(RunAction(action_type=ActionType.RUN, original_match=full_match, command=command))
            
        # Parse DELETE_FILE
        for match in cls.RE_DELETE.finditer(text):
            full_match = match.group(1)
            path = match.group(2).strip()
            actions.append(FileAction(action_type=ActionType.DELETE_FILE, original_match=full_match, path=path))
            
        # Parse MKDIR
        for match in cls.RE_MKDIR.finditer(text):
            full_match = match.group(1)
            path = match.group(2).strip()
            actions.append(FileAction(action_type=ActionType.MKDIR, original_match=full_match, path=path))
            
        # Parse MOVE_FILE
        for match in cls.RE_MOVE.finditer(text):
            full_match = match.group(1)
            src_path = match.group(2).strip()
            dst_path = match.group(3).strip()
            actions.append(FileAction(action_type=ActionType.MOVE_FILE, original_match=full_match, path=src_path, destination_path=dst_path))
            
        return actions
