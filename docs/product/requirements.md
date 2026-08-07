# AI Workspace Bridge

# Requisitos do Sistema

## 1. Objetivo
Este documento define os requisitos funcionais e não-funcionais da AI Workspace Bridge.

---

## 2. Requisitos Funcionais

### 2.1 Interface de Comunicação
- O sistema deve expor uma API REST (FastAPI) compatível com a especificação da OpenAI (`/v1/chat/completions`).
- O sistema deve suportar roteamento de prompts via tags (`!gpt`, `!claude`, `!gemini`, `!deepseek`).

### 2.2 Automação de Navegador
- O sistema deve utilizar uma instância isolada do navegador via Playwright (`BrowserDaemon`).
- O sistema deve injetar prompts diretamente nas interfaces web suportadas (ChatGPT, Claude, Gemini, DeepSeek).
- O sistema deve extrair as respostas geradas utilizando a área de transferência (`ClipboardExtractor`).

### 2.3 Agente Autônomo (AACP)
- O sistema deve interceptar tags estruturadas do protocolo AACP (`<<<FILE_CREATE>>>`, `<<<RUN>>>`, etc).
- O sistema deve criar, editar e apagar arquivos locais conforme instruído pelas respostas da IA.
- Comandos destrutivos ou execução de shell (`<<<RUN>>>`) devem solicitar confirmação interativa do usuário via terminal (`[S/n]`).

---

## 3. Requisitos Não-Funcionais

### 3.1 Portabilidade
- O sistema deve rodar de forma nativa em Windows sem requerer configurações complexas.
- O sistema não deve exigir chaves de API pagas, utilizando as sessões web ativas do usuário.

### 3.2 Segurança
- A Bridge deve operar estritamente no diretório autorizado (`BRIDGE_WORKSPACE_DIR` ou `os.getcwd()`).
- Nenhum dado deve ser enviado para serviços de terceiros além da aba do navegador aberta.
