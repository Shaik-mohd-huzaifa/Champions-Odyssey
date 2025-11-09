# Champions Odyssey - FastAPI Server

This is the backend server for Champions Odyssey, built with FastAPI and integrated with AWS Bedrock using LangChain.

## Features

- FastAPI backend with automatic API documentation
- AWS Bedrock integration for AI-powered features
- **LangChain Agent System with Tool Calling**
  - Intelligent tool selection based on user queries
  - 5+ built-in tools (calculator, datetime, text analysis, etc.)
  - Automatic decision-making: use tools when needed, answer directly when not
  - Comprehensive execution flow with intermediate step tracking
- Support for streaming responses
- Multi-turn conversation handling with context awareness
- CORS enabled for frontend integration
- Detailed tool usage reporting

## Setup

### 1. Create a virtual environment:
```bash
python -m venv venv
```

### 2. Activate the virtual environment:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies:
```bash
pip install -r requirements.txt
```

### 4. Configure AWS Bedrock

Copy the example environment file and configure your AWS credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your AWS credentials:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

**AWS Bedrock Access:**
- Ensure you have AWS Bedrock access enabled in your AWS account
- Request model access for Claude models in the AWS Bedrock console
- Your AWS IAM user/role needs `bedrock:InvokeModel` permission

**Alternative: AWS CLI Configuration**

Instead of setting credentials in `.env`, you can use AWS CLI configuration:

```bash
aws configure
```

This will store credentials in `~/.aws/credentials` which boto3 will automatically use.

## Running the Server

Start the development server:
```bash
uvicorn main:app --reload
```

The server will be available at `http://localhost:8000`

## Agent System Overview

The server uses a **LangChain Agent** that intelligently decides when to use tools and when to answer directly.

### How It Works

1. **User Query** → Sent to the agent
2. **Agent Analysis** → Determines if tools are needed
3. **Tool Selection** → Chooses appropriate tool(s) if needed
4. **Execution** → Runs tools and/or generates response
5. **Response** → Returns answer with tool usage details

### Available Tools

The agent has access to these tools:

| Tool | Purpose | Example Query |
|------|---------|---------------|
| **calculator** | Mathematical calculations | "What is 1234 * 5678?" |
| **get_current_datetime** | Current date/time information | "What time is it?" |
| **text_analyzer** | Text statistics (word count, etc.) | "Analyze this text: 'Hello world!'" |
| **champions_knowledge_base** | Project information | "What is Champions Odyssey?" |
| **string_operations** | Text manipulation | "Convert 'hello' to uppercase" |

### Agent Decision Making

- **Uses tools for**: Math, current time, text analysis, project info, string operations
- **Answers directly for**: General knowledge, explanations, conversations, advice
- **Can chain tools**: Multiple tools for complex queries

## API Documentation

Once the server is running, you can access:
- Interactive API docs (Swagger UI): `http://localhost:8000/docs`
- Alternative API docs (ReDoc): `http://localhost:8000/redoc`

## Available Endpoints

### General Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check endpoint
- `GET /api/hello` - Sample API endpoint

### AI Agent Endpoints

#### Chat with Agent (Single Message)
- `POST /api/agent/chat`
- Send a single message to the agent, which will decide whether to use tools or answer directly
- Returns response with tool usage information
- Request body:
  ```json
  {
    "message": "What is 123 * 456?"
  }
  ```
- Response:
  ```json
  {
    "response": "The result of 123 * 456 is 56,088",
    "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "tools_used": [
      {
        "tool": "calculator",
        "input": "123 * 456",
        "output": "56088"
      }
    ],
    "used_tools": true
  }
  ```

#### Multi-turn Conversation
- `POST /api/agent/conversation`
- Handle multi-turn conversations with context awareness
- Agent can use tools based on conversation flow
- Request body:
  ```json
  {
    "messages": [
      {"role": "user", "content": "My favorite number is 7"},
      {"role": "assistant", "content": "That's a great number!"},
      {"role": "user", "content": "Multiply it by 8"}
    ]
  }
  ```
- Response includes tool usage if calculator was used

#### Streaming Response
- `POST /api/agent/stream`
- Get streaming responses from the agent with real-time tool usage indicators
- Request body:
  ```json
  {
    "message": "What is 100 + 200?"
  }
  ```
- Response streams text including tool usage notifications like `[Using tool: calculator]`

#### Get Available Models
- `GET /api/agent/models`
- Get list of available models and current model configuration

#### Get Available Tools
- `GET /api/agent/tools`
- Get list of all tools the agent can use with their descriptions
- Response:
  ```json
  {
    "tools": [
      {
        "name": "calculator",
        "description": "Performs mathematical calculations..."
      }
    ],
    "count": 5
  }
  ```

## Example Usage

### Using cURL

**Simple chat (no tools needed):**
```bash
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the capital of France?"}'
```

**Chat with tool usage (calculator):**
```bash
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 1234 * 5678?"}'
```

**Get current time (datetime tool):**
```bash
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What time is it?"}'
```

**Conversation with context:**
```bash
curl -X POST "http://localhost:8000/api/agent/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "My favorite number is 15"},
      {"role": "assistant", "content": "That is a nice number!"},
      {"role": "user", "content": "Multiply it by 3"}
    ]
  }'
```

**Get available tools:**
```bash
curl http://localhost:8000/api/agent/tools
```

### Using Python Requests

```python
import requests

# Example 1: Simple question (no tools needed)
response = requests.post(
    "http://localhost:8000/api/agent/chat",
    json={"message": "What is the capital of France?"}
)
result = response.json()
print(f"Response: {result['response']}")
print(f"Used tools: {result['used_tools']}")  # False

# Example 2: Math calculation (uses calculator tool)
response = requests.post(
    "http://localhost:8000/api/agent/chat",
    json={"message": "Calculate 1234 * 5678"}
)
result = response.json()
print(f"Response: {result['response']}")
print(f"Tools used: {result['tools_used']}")  # Shows calculator usage

# Example 3: Current time (uses datetime tool)
response = requests.post(
    "http://localhost:8000/api/agent/chat",
    json={"message": "What's the current date and time?"}
)
print(response.json())

# Example 4: Text analysis (uses text_analyzer tool)
response = requests.post(
    "http://localhost:8000/api/agent/chat",
    json={"message": "Analyze this text: 'The quick brown fox jumps over the lazy dog'"}
)
print(response.json())

# Get available tools
tools = requests.get("http://localhost:8000/api/agent/tools")
print(f"Available tools: {tools.json()['count']}")
for tool in tools.json()['tools']:
    print(f"  - {tool['name']}: {tool['description'][:50]}...")

# Get available models
models = requests.get("http://localhost:8000/api/agent/models")
print(models.json())
```

### Agent Execution Flow Examples

**Example 1: Direct Answer (No Tools)**
```
User: "What is Python?"
Agent: [Analyzes query] → [No tools needed] → [Answers directly]
Response: "Python is a high-level programming language..."
tools_used: []
```

**Example 2: Calculator Tool**
```
User: "What is 25 * 48?"
Agent: [Analyzes query] → [Needs calculator] → [Calls calculator("25 * 48")] → [Gets "1200"] → [Formats response]
Response: "25 multiplied by 48 equals 1,200"
tools_used: [{"tool": "calculator", "input": "25 * 48", "output": "1200"}]
```

**Example 3: Multiple Context with Tools**
```
User: "My budget is $500. If I buy 3 items at $145 each, how much is left?"
Agent: [Analyzes] → [Needs calculator] → [Calls calculator("3 * 145")] → [Gets "435"] → [Calls calculator("500 - 435")] → [Gets "65"] → [Formats response]
Response: "If you buy 3 items at $145 each, you'll spend $435, leaving you with $65 from your $500 budget"
tools_used: [multiple calculator calls]
```

## Configuration

Edit `.env` to customize settings:

- `AWS_REGION`: AWS region (default: us-east-1)
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `BEDROCK_MODEL_ID`: Bedrock model to use
- `BEDROCK_MAX_TOKENS`: Maximum tokens in response (default: 4096)
- `BEDROCK_TEMPERATURE`: Response temperature 0-1 (default: 0.7)
- `CORS_ORIGINS`: Allowed CORS origins

## Available Bedrock Models

- `anthropic.claude-3-5-sonnet-20241022-v2:0` (recommended)
- `anthropic.claude-3-5-sonnet-20240620-v1:0`
- `anthropic.claude-3-opus-20240229-v1:0`
- `anthropic.claude-3-haiku-20240307-v1:0`
- `anthropic.claude-v2:1`
- `anthropic.claude-v2`
- `anthropic.claude-instant-v1`

## Troubleshooting

### AWS Credentials Not Found
- Ensure `.env` file exists and contains valid AWS credentials
- Or configure AWS CLI with `aws configure`

### Bedrock Access Denied
- Check that your AWS account has Bedrock access enabled
- Request model access in AWS Bedrock console
- Verify IAM permissions include `bedrock:InvokeModel`

### Model Not Found
- Ensure the model ID in your `.env` is correct
- Check that you have requested access to that specific model in AWS Bedrock console
