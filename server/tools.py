from langchain.tools import tool
from datetime import datetime
import json
from typing import Optional


@tool
def calculator(expression: str) -> str:
    """
    Performs mathematical calculations. Use this tool when the user asks for
    mathematical operations like addition, subtraction, multiplication, division,
    or more complex math expressions.

    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 2", "10 * 5 + 3")

    Returns:
        The result of the calculation

    Example:
        calculator("25 * 4") -> "100"
        calculator("(100 + 50) / 2") -> "75.0"
    """
    try:
        # Safe evaluation of mathematical expressions
        # Remove any potentially harmful characters
        safe_expression = expression.replace("^", "**")
        allowed_chars = set("0123456789+-*/(). ")

        if not all(c in allowed_chars for c in safe_expression):
            return f"Error: Invalid characters in expression. Only numbers and basic operators (+, -, *, /, ()) are allowed."

        result = eval(safe_expression)
        return str(result)
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error calculating expression: {str(e)}"


@tool
def get_current_datetime(format: Optional[str] = None) -> str:
    """
    Returns the current date and time. Use this tool when the user asks about
    the current date, time, day of the week, or any temporal information.

    Args:
        format: Optional format string. If not provided, returns a friendly format.
                Examples: "%Y-%m-%d", "%H:%M:%S", "%A, %B %d, %Y"

    Returns:
        Current date and time in the requested format

    Example:
        get_current_datetime() -> "November 9, 2025, 5:30 PM"
        get_current_datetime("%Y-%m-%d") -> "2025-11-09"
    """
    try:
        now = datetime.now()

        if format:
            return now.strftime(format)
        else:
            # Default friendly format
            return now.strftime("%B %d, %Y at %I:%M %p")
    except Exception as e:
        return f"Error getting current date/time: {str(e)}"


@tool
def text_analyzer(text: str) -> str:
    """
    Analyzes text and provides statistics like word count, character count,
    and sentence count. Use this tool when the user wants to analyze text properties.

    Args:
        text: The text to analyze

    Returns:
        JSON string with text statistics

    Example:
        text_analyzer("Hello world! How are you?") ->
        '{"word_count": 5, "character_count": 25, "sentence_count": 2}'
    """
    try:
        word_count = len(text.split())
        character_count = len(text)
        character_count_no_spaces = len(text.replace(" ", ""))
        sentence_count = text.count('.') + text.count('!') + text.count('?')

        result = {
            "word_count": word_count,
            "character_count": character_count,
            "character_count_no_spaces": character_count_no_spaces,
            "sentence_count": max(sentence_count, 1),  # At least 1 sentence
            "average_word_length": round(character_count_no_spaces / max(word_count, 1), 2)
        }

        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error analyzing text: {str(e)}"


@tool
def champions_knowledge_base(query: str) -> str:
    """
    Retrieves information about the Champions Odyssey project, its features,
    and technical details. Use this tool when the user asks about the project itself,
    its capabilities, or technical implementation.

    Args:
        query: The question about Champions Odyssey

    Returns:
        Information about the project

    Example:
        champions_knowledge_base("What is this project?") ->
        "Champions Odyssey is a full-stack application..."
    """
    knowledge = {
        "project": "Champions Odyssey is a full-stack application built with React (TypeScript) frontend and FastAPI backend, integrated with AWS Bedrock for AI capabilities.",
        "features": [
            "React TypeScript frontend for modern UI",
            "FastAPI backend with async support",
            "AWS Bedrock integration for AI features",
            "LangChain for AI agent orchestration",
            "Tool-calling agent system for intelligent task routing",
            "Streaming responses support",
            "Multi-turn conversations with context"
        ],
        "technologies": {
            "frontend": "React with TypeScript",
            "backend": "FastAPI (Python)",
            "ai": "AWS Bedrock with Claude models",
            "orchestration": "LangChain",
            "deployment": "Supports both local and cloud deployment"
        },
        "endpoints": [
            "POST /api/agent/chat - Single message chat",
            "POST /api/agent/conversation - Multi-turn conversation",
            "POST /api/agent/stream - Streaming responses",
            "GET /api/agent/models - List available AI models"
        ]
    }

    query_lower = query.lower()

    if any(word in query_lower for word in ["what", "about", "project", "application"]):
        return knowledge["project"]
    elif any(word in query_lower for word in ["feature", "capability", "can do"]):
        return f"Champions Odyssey features:\n" + "\n".join(f"- {f}" for f in knowledge["features"])
    elif any(word in query_lower for word in ["technology", "tech stack", "built with"]):
        return f"Technology stack:\n" + "\n".join(f"- {k}: {v}" for k, v in knowledge["technologies"].items())
    elif any(word in query_lower for word in ["endpoint", "api", "route"]):
        return "Available API endpoints:\n" + "\n".join(f"- {e}" for e in knowledge["endpoints"])
    else:
        return knowledge["project"] + "\n\nFor more specific information, ask about features, technologies, or endpoints."


@tool
def string_operations(operation: str, text: str, *args) -> str:
    """
    Performs various string operations like uppercase, lowercase, reverse, etc.
    Use this tool when the user wants to manipulate or transform text.

    Args:
        operation: The operation to perform (uppercase, lowercase, reverse, count, replace)
        text: The text to operate on
        *args: Additional arguments for operations like replace

    Returns:
        The transformed text

    Example:
        string_operations("uppercase", "hello") -> "HELLO"
        string_operations("reverse", "hello") -> "olleh"
    """
    try:
        operation = operation.lower()

        if operation == "uppercase":
            return text.upper()
        elif operation == "lowercase":
            return text.lower()
        elif operation == "reverse":
            return text[::-1]
        elif operation == "title":
            return text.title()
        elif operation == "count":
            if args:
                return f"'{args[0]}' appears {text.count(args[0])} times in the text"
            return f"Text length: {len(text)} characters"
        elif operation == "replace" and len(args) >= 2:
            return text.replace(args[0], args[1])
        else:
            return f"Unknown operation: {operation}. Supported: uppercase, lowercase, reverse, title, count, replace"
    except Exception as e:
        return f"Error performing string operation: {str(e)}"


# List of all available tools
ALL_TOOLS = [
    calculator,
    get_current_datetime,
    text_analyzer,
    champions_knowledge_base,
    string_operations
]
