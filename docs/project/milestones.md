# AI Workspace Bridge

# Milestones

## Objetivo

Este documento define as milestones oficiais do AI Workspace Bridge.

As milestones representam grandes entregas evolutivas da plataforma e organizam a implementação da V1 e o avanço para a V2.

Cada milestone possui:

- objetivo;
- escopo;
- entregas esperadas;
- dependências;
- critério de conclusão.

A implementação deve seguir obrigatoriamente a ordem definida neste documento.

---

# Visão Geral

A evolução da AI Workspace Bridge está organizada nas seguintes milestones:

```text
Milestone 0
Product Definition

        ↓

Milestone 1
Foundation & Local API

        ↓

Milestone 2
Browser Integration (Playwright)

        ↓

Milestone 3
TextFeeder (Injeção de Prompts)

        ↓

Milestone 4
ClipboardExtractor (Extração de Respostas)

        ↓

Milestone 5
Prompt Routing & Registry

        ↓

Milestone 6
Configuration System (YAML)

        ↓

Milestone 7
Stability & V1 Conclusion

        ↓

Milestone 8
Agentic Workflow (AACP)
```

---

# Milestone 0 — Product Definition

## Objetivo
Estabelecer e congelar as definições fundamentais do produto, arquitetura e planejamento.

## Entregas
Documentação oficial (Project Charter, Requirements, Architecture, Glossary, etc).

---

# Milestone 1 — Foundation & Local API

## Objetivo
Estabelecer o servidor local (FastAPI) rodando na porta 8000 para interceptar o fluxo da IDE.

## Entregas
- `main.py` com rotas REST.
- Simulação do `/v1/chat/completions`.

---

# Milestone 2 — Browser Integration (Playwright)

## Objetivo
Conectar o servidor Python a um navegador Chromium persistente.

## Entregas
- `BrowserDaemon` como Singleton.
- Controle de abas via CDP.

---

# Milestone 3 — TextFeeder

## Objetivo
Injetar automaticamente os prompts oriundos da IDE dentro do DOM ou campo de texto do provedor de IA.

## Entregas
- Localização de inputs dinâmicos em diferentes IAs.
- Injeção de texto segura.

---

# Milestone 4 — ClipboardExtractor

## Objetivo
Burlar limitações de Shadow DOM e bloqueios de extração lendo diretamente o clipboard da máquina física após comando Ctrl+C.

## Entregas
- Automação de teclado para selecionar texto e copiar.
- Leitura do clipboard via OS.

---

# Milestone 5 — Prompt Routing & Registry

## Objetivo
Roteamento inteligente de prompts para diferentes serviços (ChatGPT, Claude, Gemini) usando tags.

## Entregas
- Sistema de Registry.
- Leitura de tags `!gpt`, `!claude`.

---

# Milestone 6 — Configuration System

## Objetivo
Parametrizar a Bridge sem hardcode, através de arquivos externos.

## Entregas
- Leitura de `config.yaml`.
- Classe `Settings` (Singleton).

---

# Milestone 7 — Stability & V1 Conclusion

## Objetivo
Refatoração, testes integrados, tratamento de falhas e congelamento da V1.

## Entregas
- Fechamento da V1.
- Documentação sincronizada.

---

# Milestone 8 — Agentic Workflow (AACP)

## Objetivo
Transformar a Bridge de um "Proxy Passivo" para um "Executor Ativo", permitindo que a IA altere o Workspace (criação de arquivos, edição, execução de shell).

## Entregas
- Resolução de Workdir.
- AACP Parser (RegEx).
- File Executor.
- Shell Executor com interceptação interativa (Autorização).
- Mutação de Response devolvida à IDE.

---

# Regras das Milestones

## Ordem obrigatória
Milestones devem ser executadas sequencialmente.

Não é permitido:
- iniciar uma milestone futura;
- criar dependências antecipadas;
- implementar funcionalidades fora do escopo atual.

---

## Controle de Escopo
Cada milestone deve conter apenas:
- funcionalidades previstas;
- componentes documentados;
- entregas aprovadas.

Alterações de escopo devem gerar revisão da documentação.

---

## Critério Geral de Conclusão
Uma milestone é considerada concluída quando:
- todas as Issues relacionadas foram finalizadas;
- testes foram executados;
- documentação permanece consistente;
- arquitetura foi preservada;
- validação foi realizada.
