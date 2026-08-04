from fastapi import FastAPI


app = FastAPI(
    title="AI Workspace Bridge",
    version="0.1.0"
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ai-workspace-bridge"
    }