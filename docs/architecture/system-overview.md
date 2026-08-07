# AI Workspace Bridge

# System Overview

## 1. O que é a Bridge?

A AI Workspace Bridge é um middleware desenvolvido em Python projetado para unificar IAs web públicas (gratuitas ou pagas) diretamente na IDE do desenvolvedor, operando sem a necessidade de chaves de API (Keyless) através da automação inteligente de navegadores locais.

## 2. Princípios Chave

- **Local-First:** Todo o código, proxy e orquestração rodam no computador do usuário.
- **Session Sharing:** A Bridge aproveita o login humano existente nos navegadores suportados (Chrome/Edge), eliminando custos com tokens e barreiras de API.
- **Agentic Capability:** A Bridge não apenas retorna texto. Através do AACP (Aletheia Agent Communication Protocol), ela executa operações no sistema do usuário de forma segura.

## 3. Topologia

A aplicação funciona com um processo servidor (Uvicorn) mantendo instâncias singletons do Playwright ativas, mapeando requisições REST locais em ações DOM na web. O AgentExecutor escuta o tráfego de retorno em busca de intenções executáveis, aplicando as modificações no Workspace do usuário em tempo real.
