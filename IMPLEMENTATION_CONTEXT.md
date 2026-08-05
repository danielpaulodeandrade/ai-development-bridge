# AI Development Bridge

# IMPLEMENTATION CONTEXT

## Objetivo

Este documento orienta a implementação da V1.

Ele **não faz parte da documentação oficial** e **não substitui** qualquer documento presente na pasta `docs/`.

Seu objetivo é fornecer aos agentes de IA e aos desenvolvedores um contexto operacional para garantir que toda implementação permaneça consistente com a documentação aprovada.

---

# Status do Projeto

**Projeto:** AI Development Bridge

**Versão:** V1

**Status da Documentação:** Aprovada e Congelada

**Status da Arquitetura:** Congelada

**Status da Implementação:** Em desenvolvimento

**Milestone Atual:** Milestone 5 — Continue Integration (Ver referência em `docs/generated/Milestones.json`)

Toda implementação deve seguir rigorosamente a documentação oficial.

---

# Documentação Oficial

A documentação oficial está organizada em três grupos.

## Product

```text
docs/product/

project-charter.md
requirements.md
glossary.md
use-cases.md
workflows.md
```

---

## Architecture

```text
docs/architecture/

system-overview.md
design-principles.md
architecture.md
knowledge.md
prompt-engine.md
workers.md
providers.md
plugins.md
mcp.md
```

---

## Project

```text
docs/project/

bootstrap.md
conventions.md
development-workflow.md
implementation-guidelines.md
implementation-phases.md
roadmap.md
milestones.md
wbs.md
```

Todos esses documentos constituem a especificação oficial da V1.

---

# Fonte de Verdade

Em caso de conflito, deve ser respeitada a seguinte ordem:

1. Product
2. Architecture
3. Project
4. Código

A documentação sempre prevalece sobre a implementação existente.

---

# Arquitetura

A arquitetura da V1 encontra-se congelada.

Durante a implementação é proibido:

- criar novos módulos;
- alterar responsabilidades;
- modificar camadas;
- alterar fluxos documentados;
- introduzir padrões arquiteturais não documentados;
- antecipar funcionalidades de milestones futuras.

Qualquer proposta arquitetural deve ser considerada apenas para uma futura V2.

---

# Módulos Oficiais

Os únicos módulos oficiais da V1 são:

```text
core

workflow

workers

providers

plugins

mcp

data
```

Nenhum outro módulo deve ser criado sem atualização prévia da documentação oficial.

---

# Processo de Implementação

Antes de implementar qualquer alteração, seguir obrigatoriamente:

1. Ler a documentação relevante.
2. Compreender a implementação existente.
3. Identificar impacto.
4. Explicar a solução proposta.
5. Implementar apenas o escopo solicitado.
6. Criar ou atualizar testes.
7. Validar o resultado.
8. Aguardar aprovação antes da próxima etapa.

---

# Ordem das Milestones

A implementação deve respeitar a sequência definida no arquivo gerado pelo GitHub:

```text
docs/generated/Milestones.json
```

O agente deve **sempre** ler este arquivo JSON ao iniciar o contexto para saber qual é a próxima milestone válida e qual a sua descrição, ignorando listas estáticas antigas.

Não implementar funcionalidades pertencentes a milestones futuras.

---

# Consulta Obrigatória

Antes de qualquer implementação, consultar apenas os documentos necessários para a tarefa.

Toda resposta técnica deve indicar explicitamente quais documentos fundamentam a decisão.

Exemplo:

```text
docs/project/bootstrap.md

docs/architecture/architecture.md

docs/architecture/design-principles.md
```

---

# Implementação

Toda implementação deve:

- seguir os padrões existentes;
- reutilizar componentes sempre que possível;
- minimizar alterações;
- preservar compatibilidade;
- manter tipagem consistente;
- respeitar convenções do projeto.

Evitar reescritas completas quando pequenas alterações resolverem o problema.

---

# Testes

Sempre que aplicável:

- criar testes;
- atualizar testes existentes;
- executar validações.

O framework oficial é:

```text
pytest
```

---

# Git

As alterações devem ser rastreáveis:

```text
Documentação

↓

Milestone

↓

Issue

↓

Branch

↓

Implementação

↓

Testes

↓

Pull Request
```

---

# Regras para Agentes de IA

Todo agente deve:

- utilizar este documento apenas como contexto operacional;
- consultar a documentação oficial antes do código;
- nunca assumir requisitos ausentes;
- nunca inventar arquitetura;
- nunca criar componentes fora da documentação;
- respeitar a arquitetura congelada;
- solicitar esclarecimentos quando houver ambiguidades.

---

# Escopo

Este documento não altera o comportamento funcional do Media Studio AI.

Seu único objetivo é orientar o processo de implementação da V1 e garantir consistência entre desenvolvedores e agentes de IA.
