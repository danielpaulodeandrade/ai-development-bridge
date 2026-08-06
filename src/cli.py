import argparse
import sys
import uvicorn
from src.config import settings

def main():
    parser = argparse.ArgumentParser(description="AI Workspace Bridge CLI")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    
    # Subcomando 'start'
    start_parser = subparsers.add_parser("start", help="Inicia a API da Bridge e o Browser Daemon")
    
    args = parser.parse_args()
    
    if args.command == "start":
        host = settings.server.get("host", "0.0.0.0")
        port = int(settings.server.get("port", 8000))
        print(f"Iniciando AI Workspace Bridge em {host}:{port}...")
        uvicorn.run("src.interface_layer.main:app", host=host, port=port, reload=False)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
