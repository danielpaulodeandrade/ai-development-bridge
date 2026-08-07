# AI Workspace Bridge

# Implementation Guidelines

## Objetivo

Este documento define as diretrizes obrigatórias para implementação do AI Workspace Bridge.

O objetivo é garantir que todas as alterações realizadas no projeto mantenham:

- consistência arquitetural;
- qualidade técnica;
- previsibilidade;
- facilidade de manutenção;
- alinhamento com a documentação oficial.

Estas regras devem ser seguidas por desenvolvedores e agentes de inteligência artificial envolvidos no desenvolvimento.

---

# Princípio Fundamental

Antes de implementar qualquer alteração:

> Entender antes de modificar.

Nenhuma alteração deve ser realizada sem compreender:

- o objetivo da mudança;
- a arquitetura envolvida;
- o código existente;
- os impactos esperados.

---

# Ordem de Análise Obrigatória

Toda implementação deve seguir esta sequência:

```text
1. Issue
   |
2. Documentação relacionada
   |
3. Arquitetura existente
   |
4. Código atual
   |
5. Proposta de alteração
   |
6. Implementação
   |
7. Validação
```

A ordem não deve ser invertida.

---

# Documentação como Fonte de Verdade

A documentação oficial possui prioridade sobre o código.

Em caso de divergência:

- não assumir que o código está correto;
- verificar a documentação;
- ajustar a implementação conforme especificação.

---

# Respeito à Arquitetura

A arquitetura da V1 está congelada.

Durante a implementação não é permitido:

- criar novos módulos;
- criar novas camadas;
- alterar responsabilidades existentes;
- modificar fluxos principais;
- introduzir padrões arquiteturais não previstos.

Qualquer necessidade arquitetural deve ser tratada como proposta futura.

---

# Mudanças Mínimas

Toda implementação deve buscar a menor alteração possível.

Preferir:

- reutilização de componentes existentes;
- extensão de interfaces existentes;
- pequenas modificações isoladas.

Evitar:

- refatorações amplas sem necessidade;
- reorganizações estruturais;
- criação de abstrações prematuras.

---

# Código Novo

Todo código novo deve seguir:

- padrões existentes;
- estrutura atual do projeto;
- convenções definidas;
- tipagem adequada;
- testes correspondentes.

Código deve ser:

- simples;
- legível;
- objetivo.

---

# Tipagem

O projeto utiliza tipagem estática como padrão.

Código novo deve utilizar:

- type hints;
- modelos explícitos;
- contratos claros.

Evitar:

```python
def process(data):
    ...
```

Preferir:

```python
def process(data: ProjectData) -> Result:
    ...
```

---

# Responsabilidade Única

Cada componente deve possuir uma responsabilidade clara.

Um módulo não deve:

- executar múltiplas responsabilidades independentes;
- conhecer detalhes internos de outros módulos;
- assumir funções fora do seu domínio.

---

# Dependências

Antes de adicionar uma nova dependência:

Avaliar:

- necessidade real;
- impacto no projeto;
- manutenção;
- compatibilidade.

Não adicionar bibliotecas apenas por conveniência.

---

# Testes

Toda implementação deve considerar testes.

O desenvolvimento deve seguir:

```text
Código
 +
Teste
 +
Validação
```

Testes devem validar:

- comportamento esperado;
- casos críticos;
- integração entre componentes quando necessário.

---

# Arquivos Gerados

Arquivos gerados automaticamente não devem ser alterados manualmente.

Exemplos:

- arquivos produzidos por ferramentas;
- arquivos temporários;
- artefatos de build.

Caso seja necessário alterar um arquivo gerado:

- identificar sua origem;
- alterar o processo gerador;
- regenerar o arquivo.

---

# Configuração

Configurações devem permanecer centralizadas.

Não devem existir:

- valores fixos espalhados pelo código;
- credenciais no repositório;
- configurações duplicadas.

---

# Tratamento de Erros

Erros devem ser tratados de forma explícita.

Evitar:

```python
except:
    pass
```

Preferir:

- exceções específicas;
- mensagens claras;
- logs adequados.

---

# Logs

Logs devem auxiliar:

- diagnóstico;
- manutenção;
- análise de falhas.

Evitar:

```python
print("erro")
```

Em código definitivo.

---

# Uso de Inteligência Artificial

Agentes de IA utilizados no desenvolvimento devem seguir estas regras:

## Antes de alterar código

Devem:

- consultar documentação;
- entender contexto;
- identificar arquivos afetados;
- explicar impacto.

## Durante implementação

Devem:

- realizar alterações mínimas;
- respeitar padrões existentes;
- não inventar componentes.

## Após implementação

Devem:

- validar;
- informar arquivos alterados;
- apresentar testes realizados.

---

# Comunicação de Alterações

Toda alteração deve explicar:

## O que mudou

Descrição objetiva.

## Por que mudou

Motivação técnica.

## Impacto

Componentes afetados.

## Validação

Como foi verificado.

---

# Qualidade Esperada

Uma implementação considerada adequada deve ser:

- funcional;
- documentada;
- testada;
- simples;
- alinhada à arquitetura.

---

# Regra Final

Quando houver dúvida:

Não implementar.

Primeiro:

1. identificar a ausência;
2. consultar documentação;
3. solicitar decisão;
4. somente então alterar código.

O objetivo é preservar a integridade técnica do AI Workspace Bridge durante toda sua evolução.
