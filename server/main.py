from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from config import settings
from bedrock_service import bedrock_service

app = FastAPI(
    title="Champions Odyssey API",
    description="FastAPI backend for Champions Odyssey with AWS Bedrock integration",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    system_prompt: Optional[str] = None


class ConversationRequest(BaseModel):
    messages: List[ChatMessage]
    system_prompt: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    model: str

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Champions Odyssey API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/api/hello")
async def hello():
    """Sample API endpoint"""
    return {"message": "Hello from FastAPI!"}


# Agent AI endpoints
@app.post("/api/agent/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Send a single message to AWS Bedrock and get a response

    Args:
        request: ChatRequest with message and optional system prompt

    Returns:
        ChatResponse with the AI-generated response
    """
    try:
        response = await bedrock_service.generate_response(
            message=request.message,
            system_prompt=request.system_prompt
        )
        return ChatResponse(
            response=response,
            model=settings.bedrock_model_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bedrock error: {str(e)}")


@app.post("/api/agent/conversation", response_model=ChatResponse)
async def conversation_with_agent(request: ConversationRequest):
    """
    Handle multi-turn conversation with AWS Bedrock

    Args:
        request: ConversationRequest with message history and optional system prompt

    Returns:
        ChatResponse with the AI-generated response
    """
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        response = await bedrock_service.chat(
            messages=messages,
            system_prompt=request.system_prompt
        )
        return ChatResponse(
            response=response,
            model=settings.bedrock_model_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bedrock error: {str(e)}")


@app.post("/api/agent/stream")
async def stream_chat_with_agent(request: ChatRequest):
    """
    Stream responses from AWS Bedrock

    Args:
        request: ChatRequest with message and optional system prompt

    Returns:
        StreamingResponse with AI-generated content
    """
    async def generate():
        try:
            async for chunk in bedrock_service.stream_response(
                message=request.message,
                system_prompt=request.system_prompt
            ):
                yield chunk
        except Exception as e:
            yield f"Error: {str(e)}"

    return StreamingResponse(generate(), media_type="text/plain")


@app.get("/api/agent/models")
async def get_agent_models():
    """
    Get list of available Bedrock models

    Returns:
        List of available model IDs
    """
    try:
        models = bedrock_service.get_available_models()
        return {
            "models": models,
            "current_model": settings.bedrock_model_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching models: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
