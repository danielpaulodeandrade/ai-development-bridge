# AI Workspace Bridge

# Glossário Oficial

## 1. Visão Geral

Este documento define os termos oficiais utilizados na AI Workspace Bridge.
O objetivo é estabelecer um vocabulário comum entre desenvolvedores e a própria arquitetura do sistema.

---

## 2. Termos Principais

### 2.1 Bridge (ou Proxy)
A camada intermediária que roda localmente (via FastAPI) para interceptar as requisições HTTP da IDE (VS Code / Continue) e roteá-las para a web.

### 2.2 BrowserDaemon
Módulo responsável por gerenciar a instância única (singleton) do Playwright, garantindo que as abas do navegador permaneçam abertas para manter a sessão (login) do usuário ativa.

### 2.3 ClipboardExtractor
Estratégia utilizada pela Bridge para contornar bloqueios de DOM do ChatGPT/Claude, enviando `Ctrl+A`, `Ctrl+C` via automação de teclado e lendo o clipboard local para extrair as respostas da IA.

### 2.4 AACP (Aletheia Agent Communication Protocol)
Protocolo de comunicação baseado em tags (ex: `<<<FILE_CREATE>>>`) que permite à IA emitir comandos que a Bridge executará localmente no computador do usuário.

### 2.5 AgentExecutor
O módulo da Bridge que faz o parser (RegEx) das respostas que chegam com tags AACP e as traduz para chamadas do sistema operacional (criação de arquivos, comandos de terminal).
