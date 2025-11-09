from langchain_aws import ChatBedrock
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, Optional
import boto3
from config import settings


class BedrockService:
    """Service for interacting with AWS Bedrock using LangChain"""

    def __init__(self):
        """Initialize Bedrock service with LangChain"""
        self.bedrock_runtime = self._get_bedrock_client()
        self.llm = self._get_llm()

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
        """Get LangChain ChatBedrock instance"""
        return ChatBedrock(
            client=self.bedrock_runtime,
            model_id=settings.bedrock_model_id,
            model_kwargs={
                "max_tokens": settings.bedrock_max_tokens,
                "temperature": settings.bedrock_temperature,
            }
        )

    async def generate_response(
        self,
        message: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response from Bedrock for a single message

        Args:
            message: User message
            system_prompt: Optional system prompt to guide the model

        Returns:
            Generated response text
        """
        messages = []

        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        messages.append(HumanMessage(content=message))

        response = await self.llm.ainvoke(messages)
        return response.content

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Handle multi-turn conversation

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt

        Returns:
            Generated response text
        """
        langchain_messages = []

        if system_prompt:
            langchain_messages.append(SystemMessage(content=system_prompt))

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            elif role == "system":
                langchain_messages.append(SystemMessage(content=content))

        response = await self.llm.ainvoke(langchain_messages)
        return response.content

    async def stream_response(
        self,
        message: str,
        system_prompt: Optional[str] = None
    ):
        """
        Stream response from Bedrock

        Args:
            message: User message
            system_prompt: Optional system prompt

        Yields:
            Response chunks as they arrive
        """
        messages = []

        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        messages.append(HumanMessage(content=message))

        async for chunk in self.llm.astream(messages):
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content

    def get_available_models(self) -> List[str]:
        """
        Get list of available Bedrock models

        Returns:
            List of model IDs
        """
        # Common Bedrock models
        return [
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "anthropic.claude-3-5-sonnet-20240620-v1:0",
            "anthropic.claude-3-opus-20240229-v1:0",
            "anthropic.claude-3-haiku-20240307-v1:0",
            "anthropic.claude-v2:1",
            "anthropic.claude-v2",
            "anthropic.claude-instant-v1"
        ]


# Global instance
bedrock_service = BedrockService()
