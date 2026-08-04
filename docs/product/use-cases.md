# AI Workspace Bridge

# Use Cases

## 1. Objetivo

Este documento define os casos de uso principais do AI Workspace Bridge.

Os casos de uso representam as interações esperadas entre usuários, ferramentas externas e o sistema.

Eles servem como base para:

- definição da arquitetura;
- definição dos componentes;
- planejamento das milestones;
- validação da implementação.

---

# 2. Atores

## 2.1 Desenvolvedor

Responsável por utilizar o AI Workspace Bridge durante atividades de desenvolvimento.

Pode:

- configurar projetos;
- enviar contexto para modelos de IA;
- solicitar análises;
- receber respostas;
- aplicar alterações.

---

## 2.2 IDE

Ambiente utilizado pelo desenvolvedor.

Exemplo:

- VS Code.

Responsável por fornecer:

- arquivos abertos;
- seleção de código;
- contexto do workspace;
- comandos do usuário.

---

## 2.3 Provider de IA

Serviço responsável pelo processamento das solicitações.

Pode representar:

- API oficial;
- modelo local;
- plataforma web.

Exemplos:

- OpenAI;
- Gemini;
- Claude;
- Ollama;
- outros providers compatíveis.

---

# 3. Visão Geral dos Casos de Uso

| ID     | Caso de Uso                 | Objetivo                                     |
| ------ | --------------------------- | -------------------------------------------- |
| UC-001 | Registrar Workspace         | Configurar um projeto local                  |
| UC-002 | Enviar Contexto             | Preparar informações para IA                 |
| UC-003 | Solicitar Análise           | Obter avaliação sobre código ou documentação |
| UC-004 | Solicitar Planejamento      | Criar plano de execução                      |
| UC-005 | Receber Resposta            | Obter resultado estruturado                  |
| UC-006 | Persistir Histórico         | Manter rastreabilidade                       |
| UC-007 | Executar Workflow Assistido | Conduzir tarefas complexas                   |

---

# UC-001 — Registrar Workspace

## Objetivo

Permitir que um projeto local seja conhecido pelo AI Workspace Bridge.

## Ator Principal

Desenvolvedor.

## Pré-condições

- O projeto existe localmente.
- O usuário possui acesso ao diretório.

## Fluxo Principal

1. O usuário informa o diretório do projeto.
2. O sistema identifica o workspace.
3. O sistema registra informações básicas.
4. O workspace fica disponível para utilização.

## Resultado Esperado

O projeto pode ser utilizado como fonte de contexto.

---

# UC-002 — Enviar Contexto

## Objetivo

Permitir que informações relevantes sejam enviadas para uma IA sem processo manual de copiar e colar.

## Ator Principal

Desenvolvedor.

## Pré-condições

- Workspace registrado.
- Arquivos disponíveis.

## Fluxo Principal

1. O usuário seleciona arquivos ou diretórios.
2. O sistema coleta o contexto.
3. O usuário informa uma instrução.
4. O sistema envia a solicitação ao provider configurado.

## Resultado Esperado

A IA recebe contexto suficiente para responder.

---

# UC-003 — Solicitar Análise

## Objetivo

Permitir análise técnica de código, documentação ou estrutura de projeto.

## Ator Principal

Desenvolvedor.

## Exemplos

- revisar arquitetura;
- explicar código;
- identificar problemas;
- avaliar implementação.

## Fluxo Principal

1. O usuário seleciona o conteúdo.
2. O sistema monta o contexto.
3. A solicitação é enviada.
4. A resposta é retornada.

## Resultado Esperado

O usuário recebe uma análise técnica.

---

# UC-004 — Solicitar Planejamento

## Objetivo

Permitir que uma IA auxilie no planejamento de tarefas.

## Ator Principal

Desenvolvedor.

## Exemplos

- criar plano de implementação;
- decompor uma issue;
- sugerir etapas;
- analisar impacto.

## Fluxo Principal

1. O usuário fornece objetivo.
2. O sistema adiciona contexto do workspace.
3. O provider gera um plano.
4. O resultado é apresentado.

## Resultado Esperado

Existe um plano estruturado para execução.

---

# UC-005 — Receber Resposta Estruturada

## Objetivo

Permitir que respostas da IA sejam utilizadas pelo ambiente local.

## Ator Principal

Desenvolvedor.

## Fluxo Principal

1. O provider retorna uma resposta.
2. O sistema processa o conteúdo.
3. O resultado é disponibilizado.

## Possíveis resultados:

- texto Markdown;
- documentação;
- instruções;
- alterações propostas;
- arquivos gerados.

## Resultado Esperado

A resposta pode ser consumida sem copiar e colar manual.

---

# UC-006 — Persistir Histórico

## Objetivo

Manter registro das interações realizadas.

## Ator Principal

Sistema.

## Dados registrados:

- solicitação;
- contexto utilizado;
- provider utilizado;
- resposta;
- data da execução.

## Resultado Esperado

O histórico pode ser consultado posteriormente.

---

# UC-007 — Executar Workflow Assistido

## Objetivo

Permitir fluxos compostos envolvendo múltiplas etapas.

## Ator Principal

Desenvolvedor.

## Exemplos:

- analisar issue;
- consultar documentação;
- criar plano;
- implementar alteração;
- revisar resultado.

## Fluxo Principal

1. O usuário inicia um workflow.
2. O sistema coleta contexto.
3. O provider processa cada etapa.
4. Os resultados são organizados.

## Resultado Esperado

Uma tarefa complexa pode ser conduzida com menor intervenção manual.

---

# 4. Fluxo Principal do Sistema

O fluxo esperado da V1:

```text
Desenvolvedor

↓

IDE

↓

AI Workspace Bridge

↓

Context Collection

↓

AI Provider

↓

Resposta Estruturada

↓

Arquivo / Resultado Local
```

---

# 5. Casos de Uso Fora do Escopo da V1

Não fazem parte da primeira versão:

- treinamento de modelos;
- hospedagem própria de LLM;
- substituição completa da IDE;
- execução autônoma sem aprovação;
- automação de contas externas.

---

# 6. Critérios de Validação

Os casos de uso estarão atendidos quando:

- o desenvolvedor conseguir enviar contexto sem copiar e colar;
- múltiplos providers puderem ser utilizados;
- respostas puderem ser armazenadas localmente;
- o fluxo puder ser integrado ao desenvolvimento diário.
