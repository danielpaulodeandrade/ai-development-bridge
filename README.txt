================================================================
BEM-VINDO AO AI WORKSPACE BRIDGE
================================================================

Este é o executável standalone (portátil) da Bridge.
Ele orquestra suas contas de IA gratuitas (Gemini, Claude, DeepSeek, ChatGPT)
para que você possa usá-las na sua IDE favorita como se fossem a API da OpenAI.

----------------------------------------------------------------
CONFIGURAÇÃO INICIAL (Apenas na 1a vez)
----------------------------------------------------------------

1) Arquivo .env:
Ao rodar este executável pela primeira vez, ele criou um arquivo chamado ".env" nesta pasta.
Atualmente, a Bridge NÃO requer nenhuma chave de API! Ela orquestra as contas gratuitas que você já possui.
Esse arquivo .env serve apenas caso queira adicionar variáveis de ambiente avançadas no futuro.

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
O sistema utilizará seu Microsoft Edge ou Google Chrome nativo para máxima leveza.

DICA: Se houver conflito de autocompletar ao usar "@gpt" na sua IDE, você pode usar a exclamação no lugar, ex: "!gpt", "!claude".

Não feche a janela preta enquanto estiver programando.

----------------------------------------------------------------
AGENTIC WORKFLOW (AACP v1.0)
----------------------------------------------------------------

A Bridge permite que IAs (ChatGPT, Gemini) criem/editem arquivos e rodem comandos autonomamente na sua máquina!

Para ativar esse superpoder, copie e cole o bloco de texto abaixo nas "Instruções Personalizadas" do seu ChatGPT ou Gemini:

# AACP v1.0
Este projeto utiliza o Aletheia Agent Communication Protocol (AACP).
Sempre que sua resposta envolver qualquer ação sobre arquivos ou diretórios, utilize obrigatoriamente o protocolo abaixo.

Comandos permitidos:
<<<FILE_CREATE:path>>>
conteúdo
<<<END_FILE>>>

<<<FILE_REPLACE:path>>>
conteúdo
<<<END_FILE>>>

<<<FILE_PATCH:path>>>
patch
<<<END_PATCH>>>

<<<DELETE_FILE:path>>>
<<<MOVE_FILE:origem|destino>>>
<<<MKDIR:path>>>

<<<RUN>>>
comando
<<<END>>>

Regras:
- Nunca invente novos comandos.
- Nunca altere a sintaxe.
- Preserve exatamente os delimitadores <<< >>>.
- Todo conteúdo deve estar entre BEGIN e END correspondentes.
- Fora das tags, responda normalmente.

Bons códigos!
