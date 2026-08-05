from fastapi import FastAPI
import logging
import time
import asyncio
from pydantic import BaseModel
from typing import List, Optional

from src.browser_automation.browser_daemon import BrowserDaemon
from src.browser_automation.text_feeder import TextFeeder
from src.browser_automation.clipboard_extractor import ClipboardExtractor

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Workspace Bridge",
    version="0.2.0"
)

browser_daemon = BrowserDaemon(headless=False)
text_feeder = TextFeeder(browser_daemon)
clipboard_extractor = ClipboardExtractor(browser_daemon)

@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando BrowserDaemon na Bridge API...")
    await browser_daemon.start()

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

    # Mapear 'model' solicitado para a plataforma
    platform = "gemini"
    if "claude" in req.model.lower():
        platform = "claude"
    elif "gpt" in req.model.lower() or "chatgpt" in req.model.lower():
        platform = "chatgpt"

    logger.info(f"Roteando prompt para plataforma web: {platform}")
    
    # 1. Enviar prompt
    success = await text_feeder.send_prompt(prompt, platform=platform)
    if not success:
        return {"error": "Falha ao enviar prompt para o browser."}
        
    # 2. Extrair resposta
    logger.info("Extraindo resposta via Clipboard...")
    response_text = await clipboard_extractor.extract_last_response(platform=platform)
    
    if not response_text:
        response_text = "Falha ao extrair a resposta do navegador. Verifique a aba e o self-healing."

    # Formatar como OpenAI
    return {
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