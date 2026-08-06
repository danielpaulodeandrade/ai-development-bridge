# AI Development Bridge

Uma API de ponte universal para orquestrar IAs gratuitas hospedadas no navegador (ChatGPT, Claude, Gemini) e expô-las como um servidor REST compatível com o formato OpenAI. 

Ideal para plugar na extensão **Continue** do VS Code ou em qualquer outra IDE, sem pagar custos abusivos de API.

## Funcionalidades
- 🚀 **Roteamento Dinâmico por Papéis (Role-based Routing):** Digite `@architect` no prompt e a resposta será gerada pelo ChatGPT. Digite `@coder` e quem assume é o Claude. 
- 🤖 **Daemon Resiliente (Playwright):** Mantém a sessão ativa usando perfil persistente (você só loga uma vez).
- ⚙️ **Configurável via YAML:** Porta, fallback, chaves e perfis isolados no arquivo `config.yaml`.
- 📝 **Advanced Logging:** Salva o histórico de execução e de sessões de conversa (em `logs/history.jsonl`).

## Instalação

Certifique-se de estar usando um ambiente virtual e rode o comando na raiz do projeto:

```bash
pip install -e .
```

## Configuração

Na raiz do projeto, crie ou altere o arquivo `config.yaml`:

```yaml
server:
  host: "0.0.0.0"
  port: 8000

browser:
  headless: false
  timeout_ms: 10000

router:
  default_platform: "gemini"
  role_registry:
    gpt: "chatgpt"
    gemini: "gemini"
    claude: "claude"
    deepseek: "deepseek"
```

## Como Usar

Agora que a Bridge está instalada, você tem acesso global ao utilitário de linha de comando:

```bash
# Inicia o servidor e o Navegador na plataforma padrão (Gemini)
bridge start

# Pré-carrega uma plataforma específica na inicialização
bridge start gpt
bridge start claude
```

Isso subirá um servidor na porta `8000`. A Bridge agora suporta nativamente **Streaming Response (SSE)**, garantindo que o texto apareça em tempo real na sua IDE, assim como as APIs oficiais da OpenAI.

## Integração com VS Code (Continue)

A configuração oficial para usar a Bridge com a extensão **Continue** já está fornecida no diretório `.continue` na raiz deste repositório.

> [!IMPORTANT]
> **Você DEVE copiar o diretório `.continue` inteiro para a raiz de qualquer novo projeto que for criar.**
> Ele contém o arquivo `config.yaml` do Continue pré-configurado para se conectar com a Bridge na porta 8000 e usar o modelo `bridge-router`.

## Como interagir com as IAs
No chat do Continue (ou via atalho `Ctrl+I` direto no código), você pode mandar sua mensagem para a IA padrão, ou usar as **Platform Tags** para rotear a requisição:

- `@gpt Crie a classe Jogador...` -> Envia para o ChatGPT
- `@claude Revise este código...` -> Envia para o Claude
- `@deepseek O que são testes...` -> Envia para o DeepSeek
- `@gemini ...` -> Envia para o Gemini

*A Bridge possui fallbacks robustos para lidar com editores rich-text e extrai as respostas silenciosamente, garantindo a privacidade das suas sessões.*
