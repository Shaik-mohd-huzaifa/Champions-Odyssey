from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from config import settings
from bedrock_service import bedrock_service
from agent_service import agent_service

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


class AgentResponse(BaseModel):
    response: str
    model: str
    tools_used: List[Dict[str, Any]]
    used_tools: bool

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


# Agent AI endpoints with tool calling
@app.post("/api/agent/chat", response_model=AgentResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Send a single message to the AI agent which can use tools to answer

    The agent will analyze the query and determine if it needs to use any tools
    (calculator, datetime, text analyzer, etc.) or can answer directly.

    Args:
        request: ChatRequest with message

    Returns:
        AgentResponse with the AI-generated response and tool usage information

    Example:
        Input: {"message": "What is 123 * 456?"}
        Output: {
            "response": "The result is 56,088",
            "tools_used": [{"tool": "calculator", "input": "123 * 456", "output": "56088"}],
            "used_tools": true,
            "model": "anthropic.claude-3-5-sonnet-20241022-v2:0"
        }
    """
    try:
        result = await agent_service.process_query(query=request.message)
        return AgentResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.post("/api/agent/conversation", response_model=AgentResponse)
async def conversation_with_agent(request: ConversationRequest):
    """
    Handle multi-turn conversation with the AI agent

    The agent maintains context across the conversation and can use tools
    as needed based on the conversation flow.

    Args:
        request: ConversationRequest with message history

    Returns:
        AgentResponse with the AI-generated response and tool usage information

    Example:
        Input: {
            "messages": [
                {"role": "user", "content": "My favorite number is 7"},
                {"role": "assistant", "content": "That's a great number!"},
                {"role": "user", "content": "Multiply it by 8"}
            ]
        }
        Output: {
            "response": "7 multiplied by 8 equals 56",
            "tools_used": [{"tool": "calculator", "input": "7 * 8", "output": "56"}],
            "used_tools": true,
            "model": "..."
        }
    """
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        # Use the last message as the query and the rest as history
        if len(messages) > 0:
            current_query = messages[-1]["content"]
            history = messages[:-1] if len(messages) > 1 else None
            result = await agent_service.process_query(
                query=current_query,
                chat_history=history
            )
            return AgentResponse(**result)
        else:
            raise HTTPException(status_code=400, detail="No messages provided")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.post("/api/agent/stream")
async def stream_chat_with_agent(request: ChatRequest):
    """
    Stream responses from the AI agent

    The agent's response and tool usage will be streamed in real-time.

    Args:
        request: ChatRequest with message

    Returns:
        StreamingResponse with AI-generated content and tool usage indicators
    """
    async def generate():
        try:
            async for chunk in agent_service.stream_query(query=request.message):
                yield chunk
        except Exception as e:
            yield f"Error: {str(e)}"

    return StreamingResponse(generate(), media_type="text/plain")


@app.get("/api/agent/models")
async def get_agent_models():
    """
    Get list of available Bedrock models

    Returns:
        List of available model IDs and current configuration
    """
    try:
        models = bedrock_service.get_available_models()
        return {
            "models": models,
            "current_model": settings.bedrock_model_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching models: {str(e)}")


@app.get("/api/agent/tools")
async def get_agent_tools():
    """
    Get list of available tools the agent can use

    Returns:
        List of tools with their names and descriptions

    Example response:
        {
            "tools": [
                {
                    "name": "calculator",
                    "description": "Performs mathematical calculations..."
                },
                {
                    "name": "get_current_datetime",
                    "description": "Returns the current date and time..."
                }
            ],
            "count": 5
        }
    """
    try:
        tools = agent_service.get_available_tools()
        return {
            "tools": tools,
            "count": len(tools)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tools: {str(e)}")


@app.get("/api/agent/system-prompt")
async def get_agent_system_prompt():
    """
    Get the complete system prompt used by the agent

    This shows exactly what instructions and tool descriptions the agent sees,
    including all available tools and their detailed descriptions.

    Returns:
        The system prompt text

    Example response:
        {
            "system_prompt": "You are an intelligent AI agent...",
            "includes_tools": true,
            "tool_count": 5
        }
    """
    try:
        system_prompt = agent_service.get_system_prompt()
        tools = agent_service.get_available_tools()
        return {
            "system_prompt": system_prompt,
            "includes_tools": True,
            "tool_count": len(tools)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching system prompt: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
