from fastapi import FastAPI

app = FastAPI(
    title="DEX AI Control Center",
    description="Central API for managing DEX AI agents",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {
        "project": "DEX AI Control Center",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }
