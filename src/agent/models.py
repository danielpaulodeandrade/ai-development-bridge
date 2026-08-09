from enum import Enum
from dataclasses import dataclass
from typing import Optional

class ActionType(Enum):
    FILE_CREATE = "FILE_CREATE"
    FILE_REPLACE = "FILE_REPLACE"
    FILE_PATCH = "FILE_PATCH"
    DELETE_FILE = "DELETE_FILE"
    MOVE_FILE = "MOVE_FILE"
    MKDIR = "MKDIR"
    RUN = "RUN"

@dataclass
class AACPAction:
    """Classe base para todas as ações do AACP"""
    action_type: ActionType
    original_match: str  # The raw matched text to be removed from the response

@dataclass
class FileAction(AACPAction):
    """Ação relacionada a arquivos"""
    path: str
    content: Optional[str] = None
    destination_path: Optional[str] = None # Utilizado no MOVE_FILE

@dataclass
class RunAction(AACPAction):
    """Ação de execução de comando Shell"""
    command: str
