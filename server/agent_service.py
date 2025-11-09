from langchain_aws import ChatBedrock
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, Optional, AsyncIterator
import boto3
from config import settings
from tools import ALL_TOOLS


def create_agent_system_prompt(tools: List) -> str:
    """
    Dynamically create the system prompt with detailed tool descriptions

    Args:
        tools: List of LangChain tools available to the agent

    Returns:
        Complete system prompt with tool descriptions
    """
    # Build tool descriptions section
    tool_descriptions = []
    for tool in tools:
        tool_name = tool.name
        tool_desc = tool.description
        tool_descriptions.append(f"""### {tool_name}
{tool_desc}""")

    tools_section = "\n\n".join(tool_descriptions)

    prompt = f"""You are an intelligent AI agent for Champions Odyssey, a full-stack application with AI capabilities.

Your primary goal is to help users by:
1. Analyzing their questions and determining the best approach to answer them
2. Using available tools when necessary to provide accurate, real-time information
3. Answering directly when you have the knowledge without needing tools
4. Being conversational, helpful, and informative

## Available Tools

You have access to the following tools. Each tool has specific capabilities - read their descriptions carefully to understand when to use them:

{tools_section}

## Decision Making Process

1. **Analyze the query**: Understand what the user is asking
2. **Determine if tools are needed**:
   - Use tools for: calculations, current time/date, text analysis, string operations, project info
   - Answer directly for: general knowledge, advice, explanations, conversations
3. **Select the right tool**: Choose the most appropriate tool for the task based on the descriptions above
4. **Execute and respond**: Use the tool result to formulate a helpful response

## Guidelines

- **Be efficient**: Only use tools when necessary
- **Be accurate**: Use tools for factual, real-time data (calculations, current time, etc.)
- **Be conversational**: Maintain a friendly, helpful tone
- **Be clear**: Explain your reasoning when appropriate
- **Chain tools if needed**: You can use multiple tools for complex queries
- **Read tool descriptions**: The tool descriptions above tell you exactly what each tool does and when to use it

## Examples

**Query**: "What is 1234 * 5678?"
**Action**: Use calculator tool → "The result is 7,006,652"

**Query**: "What time is it?"
**Action**: Use get_current_datetime tool → "It's currently November 9, 2025 at 5:30 PM"

**Query**: "What is the capital of France?"
**Action**: Answer directly → "The capital of France is Paris"

**Query**: "Analyze this text: 'Hello world!'"
**Action**: Use text_analyzer tool → Provide analysis results

**Query**: "What can this application do?"
**Action**: Use champions_knowledge_base tool → Explain features

Remember: Your goal is to be helpful, accurate, and efficient. Use tools when they add value, but don't over-complicate simple questions. The tool descriptions above are your guide for when and how to use each tool."""

    return prompt


class AgentService:
    """Service for managing the LangChain agent with tool calling capabilities"""

    def __init__(self):
        """Initialize the agent service with Bedrock LLM and tools"""
        self.bedrock_runtime = self._get_bedrock_client()
        self.llm = self._get_llm()
        self.tools = ALL_TOOLS
        self.agent_executor = self._create_agent()

    def _get_bedrock_client(self):
        """Get Bedrock runtime client"""
        client_kwargs = {
            "region_name": settings.aws_region
        }

        # Add credentials if provided
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

        return boto3.client("bedrock-runtime", **client_kwargs)

    def _get_llm(self) -> ChatBedrock:
        """Get LangChain ChatBedrock instance with tool calling support"""
        return ChatBedrock(
            client=self.bedrock_runtime,
            model_id=settings.bedrock_model_id,
            model_kwargs={
                "max_tokens": settings.bedrock_max_tokens,
                "temperature": settings.bedrock_temperature,
            }
        )

    def _create_agent(self) -> AgentExecutor:
        """Create the agent executor with tools and dynamic prompt"""
        # Generate system prompt with tool descriptions
        system_prompt = create_agent_system_prompt(self.tools)

        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create the tool-calling agent
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)

        # Create the agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,  # Enable verbose logging for debugging
            handle_parsing_errors=True,
            max_iterations=5,  # Prevent infinite loops
            return_intermediate_steps=True  # Return tool usage information
        )

        return agent_executor

    async def process_query(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict:
        """
        Process a user query through the agent

        Args:
            query: User's question or request
            chat_history: Optional conversation history

        Returns:
            Dictionary with response, tool usage info, and execution details
        """
        try:
            # Prepare chat history if provided
            history_messages = []
            if chat_history:
                for msg in chat_history:
                    if msg.get("role") == "user":
                        history_messages.append(HumanMessage(content=msg.get("content", "")))
                    elif msg.get("role") == "assistant":
                        history_messages.append(AIMessage(content=msg.get("content", "")))

            # Execute the agent
            result = await self.agent_executor.ainvoke({
                "input": query,
                "chat_history": history_messages
            })

            # Extract information
            response_text = result.get("output", "")
            intermediate_steps = result.get("intermediate_steps", [])

            # Process intermediate steps to show tool usage
            tools_used = []
            for step in intermediate_steps:
                if len(step) >= 2:
                    action, observation = step
                    tools_used.append({
                        "tool": action.tool,
                        "input": action.tool_input,
                        "output": observation
                    })

            return {
                "response": response_text,
                "tools_used": tools_used,
                "model": settings.bedrock_model_id,
                "used_tools": len(tools_used) > 0
            }

        except Exception as e:
            return {
                "response": f"I encountered an error processing your request: {str(e)}",
                "tools_used": [],
                "model": settings.bedrock_model_id,
                "used_tools": False,
                "error": str(e)
            }

    async def stream_query(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncIterator[str]:
        """
        Stream the agent's response

        Args:
            query: User's question or request
            chat_history: Optional conversation history

        Yields:
            Response chunks as they're generated
        """
        try:
            # Prepare chat history if provided
            history_messages = []
            if chat_history:
                for msg in chat_history:
                    if msg.get("role") == "user":
                        history_messages.append(HumanMessage(content=msg.get("content", "")))
                    elif msg.get("role") == "assistant":
                        history_messages.append(AIMessage(content=msg.get("content", "")))

            # Stream the agent's execution
            async for chunk in self.agent_executor.astream({
                "input": query,
                "chat_history": history_messages
            }):
                # Extract output from different chunk types
                if "output" in chunk:
                    yield chunk["output"]
                elif "actions" in chunk:
                    # Agent is using a tool
                    for action in chunk["actions"]:
                        yield f"\n[Using tool: {action.tool}]\n"
                elif "steps" in chunk:
                    # Tool execution completed
                    for step in chunk["steps"]:
                        if len(step) >= 2:
                            action, observation = step
                            yield f"\n[Tool {action.tool} completed]\n"

        except Exception as e:
            yield f"Error: {str(e)}"

    def get_available_tools(self) -> List[Dict[str, str]]:
        """
        Get information about available tools

        Returns:
            List of tool information dictionaries
        """
        tools_info = []
        for tool in self.tools:
            tools_info.append({
                "name": tool.name,
                "description": tool.description,
            })
        return tools_info

    def get_system_prompt(self) -> str:
        """
        Get the current system prompt being used by the agent

        Returns:
            The complete system prompt with all tool descriptions
        """
        return create_agent_system_prompt(self.tools)


# Global instance
agent_service = AgentService()
