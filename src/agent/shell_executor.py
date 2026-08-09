import subprocess
import time
from typing import Optional
from src.agent.models import RunAction, ActionType
from src.config import Settings

class ShellExecutor:
    """Executa comandos Shell gerados pela IA, exigindo autorização interativa"""

    @staticmethod
    def _authorize_command(command: str) -> bool:
        """
        Trava o terminal e solicita autorização do usuário antes de rodar qualquer script.
        """
        print("\n" + "="*50)
        print("⚠️  A IA SOLICITOU A EXECUÇÃO DE UM COMANDO SHELL")
        print("="*50)
        print(f"Comando:\n{command}")
        print("="*50)
        
        while True:
            choice = input("Você autoriza esta execução? [s/N]: ").strip().lower()
            if choice in ['s', 'y', 'sim', 'yes']:
                return True
            if choice in ['n', 'nao', 'no', ''] or not choice:
                return False

    @classmethod
    def execute(cls, action: RunAction, bypass_auth: bool = False) -> str:
        """
        Solicita autorização e, se aprovada, roda o comando capturando stdout/stderr.
        `bypass_auth` existe apenas para testes unitários.
        """
        if action.action_type != ActionType.RUN:
            raise ValueError(f"Ação não suportada pelo ShellExecutor: {action.action_type}")
            
        if not bypass_auth:
            authorized = cls._authorize_command(action.command)
            if not authorized:
                return "Comando rejeitado pelo usuário por razões de segurança. Não tente novamente."
                
        workspace = Settings().get_workspace_dir()
        
        print("\nRodando comando...")
        process = subprocess.Popen(
            action.command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=workspace,
            text=True
        )
        
        # Loop de análise periódica (60s) conforme solicitado
        out = ""
        err = ""
        while True:
            try:
                out, err = process.communicate(timeout=60)
                break
            except subprocess.TimeoutExpired:
                print(f"⏱️ O comando '{action.command}' ainda está rodando (passaram-se 60s)...")
                
        # Formata o retorno para injetar de volta no contexto da IA
        result_block = f"Exit Code: {process.returncode}\n"
        if out:
            result_block += f"STDOUT:\n{out}\n"
        if err:
            result_block += f"STDERR:\n{err}\n"
            
        return result_block.strip()
