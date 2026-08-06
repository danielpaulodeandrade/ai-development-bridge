================================================================
BEM-VINDO AO AI WORKSPACE BRIDGE
================================================================

Este é o executável standalone (portátil) da Bridge.
Ele orquestra suas contas de IA gratuitas (Gemini, Claude, DeepSeek, ChatGPT)
para que você possa usá-las na sua IDE favorita como se fossem a API da OpenAI.

----------------------------------------------------------------
CONFIGURAÇÃO INICIAL (Apenas na 1a vez)
----------------------------------------------------------------

1) Arquivo .env (Chaves de API):
Ao rodar este executável pela primeira vez, ele criou um arquivo chamado ".env" nesta pasta.
Abra este arquivo no bloco de notas e preencha as chaves de API dos provedores de nuvem que desejar usar.
Para obter as chaves gratuitas, acesse:
- Groq: https://console.groq.com
- OpenRouter: https://openrouter.ai
- Cerebras: https://cloud.cerebras.ai
- Ollama Cloud: https://ollama.com

2) Configurando sua IDE (VS Code + Continue):
Também foi criada uma pasta oculta chamada ".continue" neste diretório.
Esta pasta contém o arquivo "config.yaml" pré-configurado para conectar o Continue com a Bridge.
-> COPIE A PASTA ".continue" INTEIRA E COLE NA RAIZ DO SEU NOVO PROJETO.
Ao abrir o VS Code nesse projeto, a extensão Continue lerá essa configuração automaticamente.

----------------------------------------------------------------
COMO USAR
----------------------------------------------------------------

Apenas dê 2 cliques no arquivo "bridge.exe".
Ele abrirá uma janela preta e iniciará o servidor na porta 8000.
Na primeira vez que for rodado, ele baixará o navegador Chromium em background (pode demorar 1-2 minutos).

Não feche a janela preta enquanto estiver programando.

Bons códigos!
