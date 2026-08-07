# AI Workspace Bridge

# Arquitetura Principal

## 1. Topologia do Sistema

A AI Workspace Bridge opera como um serviço local (middleware) composto por três camadas principais:

### 1.1 Interface Layer (API)
- **FastAPI / Uvicorn:** Expõe a porta local (`8000`) para a IDE (VS Code / Continue).
- **OpenAI Proxy:** Simula o padrão REST da OpenAI (`/v1/chat/completions`) para garantir compatibilidade nativa com extensões de IA.

### 1.2 Orchestration Layer
- **Router:** Processa tags como `!gpt` e `!claude` para definir o destino do fluxo.
- **AgentExecutor (AACP):** Intercepta as respostas que retornam do navegador. Faz o parse de comandos (ex: `<<<FILE_CREATE>>>`) e aciona chamadas de sistema (File I/O, Subprocess) localmente.

### 1.3 Execution Layer (BrowserDaemon)
- **Playwright Singleton:** Mantém uma instância persistente do navegador Chrome/Edge para aproveitar a sessão (login) autenticada pelo usuário humano.
- **TextFeeder:** Automação de interface que simula digitação ou injeta via DOM o prompt.
- **ClipboardExtractor:** Extrai a resposta formatada lendo a área de transferência do Sistema Operacional.

---

## 2. Fluxo de Execução (V2)

1. A IDE dispara o prompt para a Bridge.
2. A Bridge identifica a plataforma (ex: chatgpt) e a repassa para o BrowserDaemon.
3. O BrowserDaemon navega/foca na aba, injeta o texto e aguarda a geração.
4. O ClipboardExtractor recupera a resposta bruta.
5. O AgentExecutor escaneia a resposta bruta buscando tags AACP.
6. Se encontrar tags (ex: Criar arquivo), executa a ação localmente.
7. Se encontrar tag `<<<RUN>>>`, solicita permissão no console do usuário.
8. As tags executadas são removidas do texto final e um log legível em Markdown é adicionado.
9. A resposta mutada é devolvida para a IDE.
