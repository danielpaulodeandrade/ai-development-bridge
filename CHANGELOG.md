# Changelog

All notable changes to this project will be documented in this file.

---

# Version 1.0.0

## Documentation

Initial project documentation completed.

### Product

- Project Charter
- Requirements
- Glossary
- Use Cases
- Workflows

### Architecture

- System Overview
- Design Principles
- Architecture
- Providers
- Plugins
- MCP
- Knowledge
- Prompt Engine
- Workers

### Project

- Bootstrap
- Conventions
- Development Workflow
- Implementation Guidelines
- Implementation Phases
- Roadmap
- Milestones
- Work Breakdown Structure (WBS)

### Operational

- IMPLEMENTATION_CONTEXT.md
- AGENTS.md

---

## Implementation (V1 Final)

- **Streaming Response (SSE)**: Implementação do padrão OpenAI SSE para integração seamless com IDEs (como Continue).
- **Roteamento Dinâmico Declarativo**: Substituição de "roles" por Platform Tags (`@gpt`, `@claude`, `@gemini`, `@deepseek`) configuráveis via `config.yaml`.
- **Pre-loading de Plataforma**: Novo argumento de CLI (`bridge start [plataforma]`) para otimizar o tempo da primeira requisição.
- **Robustez de Injeção de Texto (Fallback)**: Mecanismo de fallback usando teclado virtual (`insert_text`) para burlar proteções de *rich-text areas* (ex: Google Gemini).
- **Smart Extraction e Privacidade Máxima**: Polling inteligente que aguarda o fim da geração, ignora prompts do usuário e utiliza seletores precisos baseados em SVG Pathing para evitar vazamentos via links públicos acidentais (ex: DeepSeek Share button).
- **Setup Automático**: Disponibilização do diretório `.continue` nativo com o perfil do Bridge pré-configurado.

---

## Status

- Documentação V1 e testes de integração com a extensão *Continue* concluídos com sucesso.
- V1.0.0 estabilizada na branch `dev`. Preparando merge para `main`.
