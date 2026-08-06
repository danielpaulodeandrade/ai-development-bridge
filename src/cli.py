import argparse
import sys
import os
import uvicorn
from src.config import settings

def auto_scaffold():
    """Extracts default configuration files if running as a PyInstaller executable and not present."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
        cwd = os.getcwd()
        
        needs_install = False
        
        # Scaffolding .env
        env_dest = os.path.join(cwd, '.env')
        if not os.path.exists(env_dest):
            import shutil
            shutil.copy(os.path.join(base_path, '.env.example'), env_dest)
            needs_install = True
            
        # Scaffolding config.yaml
        cfg_dest = os.path.join(cwd, 'config.yaml')
        if not os.path.exists(cfg_dest):
            import shutil
            shutil.copy(os.path.join(base_path, 'config.yaml'), cfg_dest)
            needs_install = True
            
        # Scaffolding README.txt
        readme_dest = os.path.join(cwd, 'README.txt')
        if not os.path.exists(readme_dest):
            import shutil
            shutil.copy(os.path.join(base_path, 'README.txt'), readme_dest)
            needs_install = True
            
        # Scaffolding .continue
        cont_dest = os.path.join(cwd, '.continue')
        if not os.path.exists(cont_dest):
            import shutil
            shutil.copytree(os.path.join(base_path, '.continue'), cont_dest, dirs_exist_ok=True)
            needs_install = True
            
        if needs_install:
            print("\n============================================================")
            print(" Estamos preparando o diretorio isolado para a execução da ferramenta.")
            print(" Fazendo download do navegador interno (Chromium).")
            print(" Aguarde, pode levar entre 1 a 2 minutos...")
            print("============================================================\n")
            
            # Run playwright install programmatically
            try:
                from playwright.__main__ import main as playwright_main
                import sys
                old_argv = sys.argv
                sys.argv = ['playwright', 'install', 'chromium']
                try:
                    playwright_main()
                except SystemExit:
                    pass
                sys.argv = old_argv
                print("\n[OK] Instalação concluída com sucesso!\n")
            except Exception as e:
                print(f"\n[AVISO] Erro ao baixar o navegador: {e}\n")


def main():
    # Scaffold if PyInstaller executable
    auto_scaffold()
    
    parser = argparse.ArgumentParser(description="AI Workspace Bridge CLI")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    
    # Subcomando 'start'
    start_parser = subparsers.add_parser("start", help="Inicia a API da Bridge e o Browser Daemon")
    start_parser.add_argument(
        "platform", 
        nargs="?", 
        default="", 
        help="Plataforma inicial para pré-carregar no navegador (ex: gpt, gemini, claude)"
    )
    
    # Se nenhum argumento for passado, default para start
    args = parser.parse_args(sys.argv[1:] if len(sys.argv) > 1 else ['start'])
    
    if args.command == "start":
        if args.platform:
            os.environ["BRIDGE_INITIAL_PLATFORM"] = args.platform
            
        host = settings.server.get("host", "0.0.0.0")
        port = int(settings.server.get("port", 8000))
        print(f"Iniciando AI Workspace Bridge em {host}:{port}...")
        uvicorn.run("src.interface_layer.main:app", host=host, port=port, reload=False)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
