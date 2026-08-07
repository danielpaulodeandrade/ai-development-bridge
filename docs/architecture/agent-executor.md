# Agent Executor Architecture (AACP)

## Visão Geral

A arquitetura da Bridge está evoluindo de um simples proxy de texto (V1) para um nó executor de comandos autônomos (V2). Esta evolução é baseada no **Aletheia Agent Communication Protocol (AACP)**.

O objetivo do `AgentExecutor` é interceptar as respostas geradas pelas IAs hospedadas (ChatGPT, Claude, etc.), buscar por tags estruturadas (AACP) e executar essas operações diretamente no sistema operacional do usuário.

---

## 1. O Protocolo AACP

O ChatGPT ou Claude deve ser instruído através de System Prompts (via Continue ou configurações do Workspace) a retornar comandos no seguinte formato:

- **Criar Arquivo:**
  ```text
  <<<FILE_CREATE:caminho/do/arquivo>>>
  conteudo
  <<<END_FILE>>>
  ```
- **Substituir Arquivo:**
  ```text
  <<<FILE_REPLACE:caminho/do/arquivo>>>
  conteudo
  <<<END_FILE>>>
  ```
- **Apagar Arquivo:**
  ```text
  <<<DELETE_FILE:caminho/do/arquivo>>>
  ```
- **Mover Arquivo:**
  ```text
  <<<MOVE_FILE:origem|destino>>>
  ```
- **Criar Diretório:**
  ```text
  <<<MKDIR:caminho/do/diretorio>>>
  ```
- **Rodar Comando (Shell):**
  ```text
  <<<RUN>>>
  comando
  <<<END>>>
  ```

---

## 2. Componente AgentExecutor

O `AgentExecutor` atua na camada de interface (`src/interface_layer/main.py`), logo após o `ClipboardExtractor` recuperar o texto bruto da IA e antes da resposta final ser formatada no padrão OpenAI e devolvida ao VS Code.

### Responsabilidades

1. **Parsing:** Analisar o texto da resposta via Expressões Regulares (`re`) buscando as tags AACP.
2. **Execução:** 
   - Utilizar a biblioteca `os` e `shutil` do Python para manipulação de arquivos.
   - Utilizar a biblioteca `subprocess` para comandos shell.
3. **Segurança (Authorization):** 
   - Ao encontrar a tag `<<<RUN>>>`, o executor obrigatoriamente pausará e solicitará confirmação do usuário no terminal (I/O padrão) antes de executar.
4. **Mutação de Resposta:** 
   - Após executar, as tags brutas no texto serão substituídas por badges amigáveis de confirmação (ex: `✅ Arquivo criado: path`).

---

## 3. Workdir Resolution

A raiz para execução de comandos e criação de arquivos será determinada dinamicamente através de uma prioridade:
1. Variável de ambiente `BRIDGE_WORKSPACE_DIR` (pode ser injetada no `.env`).
2. Fallback para `os.getcwd()` (diretório de onde o executável `bridge.exe` foi iniciado).

---

## 4. Limitações Iniciais (V2.0)

- O comando `<<<FILE_PATCH:path>>>` (diffs granulares) não será implementado na primeira iteração devido à complexidade de parsers de unified-diff. A IA será instruída a utilizar `<<<FILE_REPLACE:path>>>` para atualizar arquivos.
- A Bridge operará localmente e com os mesmos privilégios do usuário que executou o terminal.
