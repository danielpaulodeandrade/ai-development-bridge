import argparse
import sys
import os

if getattr(sys, 'frozen', False):
    # Set a persistent browser path so Playwright doesn't try to use the temporary _MEIPASS folder
    # We put it in a hidden '.pw-browsers' folder exactly where the executable is located,
    # ensuring the application remains 100% portable and leaves no traces if deleted.
    exe_dir = os.path.dirname(sys.executable)
    browser_path = os.path.join(exe_dir, '.pw-browsers')
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browser_path

import uvicorn
from src.config import settings

def auto_scaffold():
    """Extracts default configuration files if running as a PyInstaller executable and not present."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
        exe_dir = os.path.dirname(sys.executable)
        
        needs_install = False
        
        # Scaffolding .env
        env_dest = os.path.join(exe_dir, '.env')
        if not os.path.exists(env_dest):
            import shutil
            shutil.copy(os.path.join(base_path, '.env.example'), env_dest)
            needs_install = True
            
        # Scaffolding config.yaml
        cfg_dest = os.path.join(exe_dir, 'config.yaml')
        if not os.path.exists(cfg_dest):
            import shutil
            shutil.copy(os.path.join(base_path, 'config.yaml'), cfg_dest)
            needs_install = True
            
        # Scaffolding README.txt
        readme_dest = os.path.join(exe_dir, 'README.txt')
        if not os.path.exists(readme_dest):
            import shutil
            shutil.copy(os.path.join(base_path, 'README.txt'), readme_dest)
            needs_install = True
            
        # Scaffolding .continue
        cont_dest = os.path.join(exe_dir, '.continue')
        if not os.path.exists(cont_dest):
            import shutil
            shutil.copytree(os.path.join(base_path, '.continue'), cont_dest, dirs_exist_ok=True)
            needs_install = True
            
        if needs_install:
            print("\n============================================================")
            print(" AI Workspace Bridge Standalone Inicializado com Sucesso.")
            print(f" Criando ambiente isolado (.env, .continue, config.yaml) em: {exe_dir}")
            print("============================================================\n")


def main():
    # Scaffold if PyInstaller executable
    auto_scaffold()
    
    if getattr(sys, 'frozen', False):
        try:
            from dotenv import load_dotenv
            exe_env = os.path.join(os.path.dirname(sys.executable), '.env')
            if os.path.exists(exe_env):
                load_dotenv(exe_env)
        except ImportError:
            pass
    
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
    
    # Subcomando 'install_browser' (Hidden)
    subparsers.add_parser("install_browser", help=argparse.SUPPRESS)
    
    # Se nenhum argumento for passado, default para start
    args = parser.parse_args(sys.argv[1:] if len(sys.argv) > 1 else ['start'])
    
    if args.command == "install_browser":
        from playwright.__main__ import main as playwright_main
        sys.argv = ['playwright', 'install', 'chromium']
        try:
            playwright_main()
        except SystemExit:
            pass
        sys.exit(0)
    elif args.command == "start":
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
