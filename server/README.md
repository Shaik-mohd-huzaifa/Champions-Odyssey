# Champions Odyssey - FastAPI Server

This is the backend server for Champions Odyssey, built with FastAPI and integrated with AWS Bedrock using LangChain.

## Features

- FastAPI backend with automatic API documentation
- AWS Bedrock integration for AI-powered features
- LangChain for LLM orchestration
- Support for streaming responses
- Multi-turn conversation handling
- CORS enabled for frontend integration

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
- Send a single message and get an AI response
- Request body:
  ```json
  {
    "message": "What is the capital of France?",
    "system_prompt": "You are a helpful assistant." // optional
  }
  ```

#### Multi-turn Conversation
- `POST /api/agent/conversation`
- Handle multi-turn conversations with context
- Request body:
  ```json
  {
    "messages": [
      {"role": "user", "content": "Hello!"},
      {"role": "assistant", "content": "Hi! How can I help you?"},
      {"role": "user", "content": "What's the weather like?"}
    ],
    "system_prompt": "You are a helpful assistant." // optional
  }
  ```

#### Streaming Response
- `POST /api/agent/stream`
- Get streaming responses from the agent
- Request body:
  ```json
  {
    "message": "Tell me a story",
    "system_prompt": "You are a creative storyteller." // optional
  }
  ```

#### Get Available Models
- `GET /api/agent/models`
- Get list of available models and current model configuration

## Example Usage

### Using cURL

**Simple chat:**
```bash
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

**Conversation with context:**
```bash
curl -X POST "http://localhost:8000/api/agent/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "My name is Alice"},
      {"role": "assistant", "content": "Hello Alice! Nice to meet you."},
      {"role": "user", "content": "What is my name?"}
    ]
  }'
```

### Using Python Requests

```python
import requests

# Simple chat
response = requests.post(
    "http://localhost:8000/api/agent/chat",
    json={
        "message": "Explain quantum computing in simple terms",
        "system_prompt": "You are a physics teacher."
    }
)
print(response.json())

# Get available models
models = requests.get("http://localhost:8000/api/agent/models")
print(models.json())
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
