# AI Workspace Bridge

# Project Conventions

## Objetivo

Este documento define as convenções utilizadas no desenvolvimento do AI Workspace Bridge.

As convenções têm como objetivo garantir:

- consistência do código;
- previsibilidade da estrutura;
- facilidade de manutenção;
- colaboração entre desenvolvedores e agentes de IA;
- padronização dos processos.

---

# Princípios Gerais

O desenvolvimento deve seguir os seguintes princípios:

## Simplicidade

Preferir soluções simples e claras.

Evitar:

- abstrações prematuras;
- complexidade desnecessária;
- frameworks sem necessidade;
- padrões arquiteturais não documentados.

---

## Consistência

Novas implementações devem seguir padrões já existentes.

Antes de criar novos componentes:

- verificar estruturas existentes;
- reutilizar padrões definidos;
- consultar documentação oficial.

---

## Rastreabilidade

Toda alteração deve possuir origem identificável:

```text
Documentação

↓

Milestone

↓

Issue

↓

Implementação

↓

Teste
```

---

# Linguagem

## Código

O código deve utilizar:

- Python 3.12;
- nomes em inglês;
- documentação técnica em inglês quando aplicável.

Exemplo:

```python
class WorkflowEngine:
    pass
```

---

## Documentação

A documentação oficial deve ser escrita em:

- português.

Exemplo:

```text
docs/architecture/architecture.md
```

---

## Prompts de IA

Prompts enviados para modelos de IA devem preferencialmente utilizar:

- inglês.

Motivo:

- maior compatibilidade entre modelos;
- melhor interpretação técnica;
- consistência entre providers.

---

# Estrutura de Código

O projeto utiliza estrutura:

```text
src layout
```

Padrão:

```text
src/
└── media_studio/
    ├── core/
    ├── workflow/
    ├── workers/
    ├── providers/
    ├── plugins/
    ├── mcp/
    └── data/
```

Novos módulos somente podem ser criados se estiverem previstos na documentação oficial.

---

# Python

## Versão

Versão oficial:

```text
Python >= 3.12
```

---

## Estilo

Seguir:

- PEP 8;
- type hints;
- código legível;
- funções pequenas;
- responsabilidades claras.

Exemplo:

```python
def load_configuration(path: Path) -> Configuration:
    ...
```

---

# Tipagem

A tipagem deve ser utilizada sempre que possível.

Preferir:

```python
def execute(workflow: Workflow) -> Result:
    ...
```

Evitar:

```python
def execute(data):
    ...
```

---

# Testes

Framework oficial:

```text
pytest
```

Toda implementação deve possuir testes quando aplicável.

Estrutura:

```text
tests/

├── test_core.py
├── test_workflow.py
├── test_providers.py
└── test_plugins.py
```

---

# Documentação de Código

Código complexo deve possuir documentação explicando:

- objetivo;
- responsabilidade;
- limitações.

Evitar comentários descrevendo apenas o código.

Ruim:

```python
# increment counter
counter += 1
```

Bom:

```python
# Tracks processed workflows to support execution monitoring.
counter += 1
```

---

# Nomenclatura

## Arquivos

Usar:

```text
snake_case
```

Exemplo:

```text
workflow_engine.py
```

---

## Classes

Usar:

```text
PascalCase
```

Exemplo:

```python
class WorkflowEngine:
    pass
```

---

## Funções e variáveis

Usar:

```text
snake_case
```

Exemplo:

```python
workflow_status = "running"
```

---

# Git

## Branches

Padrão:

```text
<tipo>/<descricao>
```

Exemplos:

```text
feature/m1-001-project-bootstrap

fix/config-loading-error

docs/update-architecture
```

---

## Tipos de branch

Permitidos:

```text
feature/
fix/
docs/
refactor/
test/
chore/
```

---

# Commits

Commits devem ser pequenos e objetivos.

Formato:

```text
<tipo>: descrição
```

Exemplos:

```text
feat: implement workflow engine

fix: correct configuration loading

docs: update architecture documentation
```

---

# Pull Requests

Toda implementação deve possuir:

- descrição da alteração;
- referência da Issue;
- impacto identificado;
- testes executados.

---

# Alterações Arquiteturais

Alterações de arquitetura são proibidas durante a V1.

Não permitido:

- criar módulos novos;
- alterar responsabilidades;
- criar novas camadas;
- modificar fluxos definidos.

Qualquer alteração deve ser proposta como evolução futura.

---

# Dependências

Antes de adicionar uma dependência:

Avaliar:

- necessidade real;
- impacto;
- manutenção;
- compatibilidade Python;
- licença.

Evitar dependências desnecessárias.

---

# Configuração

Configurações devem permanecer centralizadas.

Não permitido:

- valores fixos espalhados pelo código;
- secrets versionados;
- configurações duplicadas.

---

# Agentes de IA

Agentes de IA devem:

- consultar documentação antes de implementar;
- respeitar arquitetura congelada;
- explicar impacto das alterações;
- propor mudanças mínimas;
- criar testes;
- aguardar validação.

---

# Arquivos Gerados

Arquivos gerados automaticamente devem ser identificados.

Não modificar manualmente sem confirmação:

- arquivos de build;
- caches;
- artefatos;
- arquivos temporários.

---

# Qualidade

Antes de considerar uma tarefa concluída:

Validar:

```text
Documentação

↓

Implementação

↓

Testes

↓

Revisão

↓

Commit
```

---

# Objetivo Final

As convenções garantem que o AI Workspace Bridge permaneça organizado, previsível e sustentável durante toda sua evolução.
