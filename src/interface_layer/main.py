from fastapi import FastAPI
import logging
import time
import asyncio
from pydantic import BaseModel
from typing import List, Optional

from src.browser_automation.browser_daemon import BrowserDaemon
from src.browser_automation.text_feeder import TextFeeder
from src.browser_automation.clipboard_extractor import ClipboardExtractor
from src.browser_automation.dom_streamer import DOMStreamer
from src.config import settings
from src.history import history_logger

from src.agent.parser import AACPParser
from src.agent.models import ActionType, FileAction, RunAction
from src.agent.file_executor import FileExecutor
from src.agent.shell_executor import ShellExecutor
from src.agent.stream_interceptor import intercept_aacp_stream

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Workspace Bridge",
    version="1.0.1"
)

browser_daemon = BrowserDaemon()
text_feeder = TextFeeder(browser_daemon)
clipboard_extractor = ClipboardExtractor(browser_daemon)
dom_streamer = DOMStreamer(browser_daemon)

@app.on_event("startup")
async def startup_event():
    import os
    logger.info("Iniciando BrowserDaemon na Bridge API...")
    await browser_daemon.start()
    
    initial_platform = os.environ.get("BRIDGE_INITIAL_PLATFORM")
    if not initial_platform:
        initial_platform = settings.router.get("default_platform", "gpt")
        
    URLS = {
        "gemini": "https://gemini.google.com",
        "gpt": "https://chatgpt.com",
        "chatgpt": "https://chatgpt.com",
        "claude": "https://claude.ai/new",
        "deepseek": "https://chat.deepseek.com",
        "qwen": "https://chat.qwen.ai/",
        "kimi": "https://www.kimi.com/",
        "deepai": "https://deepai.org/chat",
        "grok": "https://grok.com/",
        "chatx": "https://chatx.ai/"
    }
    
    target_url = URLS.get(initial_platform.lower())
    if target_url:
        logger.info(f"Pré-carregando plataforma inicial: {initial_platform}")
        try:
            await browser_daemon.navigate(target_url)
        except Exception as e:
            logger.error(f"Erro no pré-carregamento: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Encerrando BrowserDaemon...")
    await browser_daemon.stop()

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ai-workspace-bridge"
    }

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    logger.info(f"Recebida requisição para o modelo: {req.model}")
    
    # Extrai o prompt do último usuário
    prompt = ""
    for msg in reversed(req.messages):
        if msg.role == "user":
            prompt = msg.content
            break
            
    if not prompt:
        prompt = "Hello"

    # Extração de Workspace dinâmico
    import re
    dynamic_workspace = None
    for msg in req.messages:
        ws_match = re.search(r'<BRIDGE_WORKSPACE>(.*?)</BRIDGE_WORKSPACE>', msg.content, re.IGNORECASE)
        if ws_match:
            dynamic_workspace = ws_match.group(1).strip()
            # Limpa a tag para não ir junto se estiver no user prompt
            prompt = re.sub(r'<BRIDGE_WORKSPACE>.*?</BRIDGE_WORKSPACE>', '', prompt, flags=re.IGNORECASE).strip()
            break

    # Extração de Role Tags para Multi AI Orchestration
    ROLE_REGISTRY = settings.router.get("role_registry", {})
    
    # Default platform fallback
    platform = settings.router.get("default_platform", "gpt")
    
    roles_pattern = "|".join(ROLE_REGISTRY.keys())
    # Suporta tanto @tag quanto !tag
    role_match = re.search(rf'[@!]({roles_pattern})\b', prompt, re.IGNORECASE)
    
    if role_match:
        role = role_match.group(1).lower()
        platform = ROLE_REGISTRY.get(role, platform)
            
        logger.info(f"Role tag detectada (modelo: {role})! Sobrescrevendo roteamento para {platform}.")
        # Remove a tag do prompt original para higienização
        prompt = re.sub(rf'[@!]({roles_pattern})\b', '', prompt, flags=re.IGNORECASE).strip()
    else:
        # Fallback para o modelo da requisição
        if "claude" in req.model.lower():
            platform = "claude"
        elif "gpt" in req.model.lower() or "chatgpt" in req.model.lower():
            platform = "chatgpt"

    logger.info(f"Roteando prompt para plataforma web: {platform}")
    
    URLS = {
        "gemini": "https://gemini.google.com",
        "gpt": "https://chatgpt.com",
        "chatgpt": "https://chatgpt.com",
        "claude": "https://claude.ai",
        "deepseek": "https://chat.deepseek.com",
        "qwen": "https://chat.qwen.ai/",
        "kimi": "https://www.kimi.com/",
        "deepai": "https://deepai.org/chat",
        "grok": "https://grok.com/",
        "chatx": "https://chatx.ai/"
    }
    
    target_url = URLS.get(platform)
    if target_url:
        try:
            await browser_daemon.navigate(target_url)
        except Exception as e:
            logger.error(f"Erro ao navegar para {target_url}: {e}")
            return {"error": f"Falha ao navegar para {platform}."}
    
    # 1. Enviar prompt
    success = await text_feeder.send_prompt(prompt, platform=platform)
    if not success:
        return {"error": "Falha ao enviar prompt para o browser."}
        
    if req.stream:
        # V2 Streaming Engine
        logger.info("Iniciando extração em tempo real via DOMStreamer...")
        from fastapi.responses import StreamingResponse
        import json
        
        async def generate():
            response_id = f"chatcmpl-{int(time.time())}"
            created_at = int(time.time())
            
            chunk_role = {
                "id": response_id,
                "object": "chat.completion.chunk",
                "created": created_at,
                "model": req.model,
                "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}]
            }
            yield f"data: {json.dumps(chunk_role)}\n\n"
            
            full_response_text = ""
            
            # Usamos True por padrão para habilitar o Interceptor (Modo Híbrido: Streama o texto normal, mas pausa e processa as tags AACP de forma invisível)
            realtime = settings.agent.get("realtime_extraction", True)
            
            if realtime:
                # Option 1: AACP Stream Interceptor (Real-time)
                async for delta in intercept_aacp_stream(dom_streamer.stream_response(platform=platform)):
                    if not delta:
                        continue
                    full_response_text += delta
                    chunk_content = {
                        "id": response_id,
                        "object": "chat.completion.chunk",
                        "created": created_at,
                        "model": req.model,
                        "choices": [{"index": 0, "delta": {"content": delta}, "finish_reason": None}]
                    }
                    yield f"data: {json.dumps(chunk_content)}\n\n"
            else:
                # Option 3: Hybrid Incremental Extraction
                # Mantém um set de ações que já foram executadas para não repeti-las durante o stream
                executed_matches = set()
                
                async for delta in dom_streamer.stream_response(platform=platform):
                    if not delta:
                        continue
                    full_response_text += delta
                    chunk_content = {
                        "id": response_id,
                        "object": "chat.completion.chunk",
                        "created": created_at,
                        "model": req.model,
                        "choices": [{"index": 0, "delta": {"content": delta}, "finish_reason": None}]
                    }
                    yield f"data: {json.dumps(chunk_content)}\n\n"
                    
                    # Varredura Incremental: Tenta extrair ações completas do texto acumulado
                    try:
                        actions = AACPParser.parse(full_response_text)
                        badges = ""
                        for action in actions:
                            # Se a ação já foi executada neste stream, ignora
                            if action.original_match in executed_matches:
                                continue
                                
                            if isinstance(action, FileAction):
                                logger.info(f"Executando FileAction (híbrido): {action.action_type.value} no workspace: {dynamic_workspace or 'default'}")
                                res = FileExecutor.execute(action, dynamic_workspace)
                            elif isinstance(action, RunAction):
                                logger.info("Executando RunAction (híbrido)...")
                                res = ShellExecutor.execute(action)
                            else:
                                res = "Executed."
                            badges += f"\n\n> **Agent Execution:**\n> ```text\n> {res}\n> ```\n"
                            
                            # Marca como executado para não executar novamente na próxima letra do stream
                            executed_matches.add(action.original_match)
                        
                        if badges:
                            chunk_content = {
                                "id": response_id,
                                "object": "chat.completion.chunk",
                                "created": created_at,
                                "model": req.model,
                                "choices": [{"index": 0, "delta": {"content": badges}, "finish_reason": None}]
                            }
                            yield f"data: {json.dumps(chunk_content)}\n\n"
                            full_response_text += badges
                    except Exception as e:
                        logger.error(f"Erro no incremental parsing (híbrido): {e}")
            
            history_logger.log_interaction(platform, prompt, full_response_text)
            
            chunk_end = {
                "id": response_id,
                "object": "chat.completion.chunk",
                "created": created_at,
                "model": req.model,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
            }
            yield f"data: {json.dumps(chunk_end)}\n\n"
            yield "data: [DONE]\n\n"
            
        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        # V1 Clipboard Extractor (Fallback / Non-Streaming)
        logger.info("Extraindo resposta via Clipboard...")
        response_text = await clipboard_extractor.extract_last_response(prompt=prompt, platform=platform)
        
        if not response_text:
            response_text = "Falha ao extrair a resposta do navegador. Verifique a aba e o self-healing."
            
        # --- AACP Mutation ---
        actions = AACPParser.parse(response_text)
        for action in actions:
            result_msg = ""
            if isinstance(action, FileAction):
                logger.info(f"Executando FileAction: {action.action_type.value} no workspace: {dynamic_workspace or 'default'}")
                result_msg = FileExecutor.execute(action, dynamic_workspace)
            elif isinstance(action, RunAction):
                logger.info("A mutação de resposta está aguardando o fim do comando shell...")
                result_msg = ShellExecutor.execute(action)
                
            badge = f"\n> **Agent Execution:**\n> ```text\n> {result_msg}\n> ```\n"
            response_text = response_text.replace(action.original_match, badge)
        # -----------------------
            
        history_logger.log_interaction(platform, prompt, response_text)

        response_data = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": req.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text,
                },
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": len(prompt)//4, "completion_tokens": len(response_text)//4, "total_tokens": (len(prompt)+len(response_text))//4}
        }
        return response_data