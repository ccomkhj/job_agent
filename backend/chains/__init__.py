# LangChain chains and configuration
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from langchain_openai import ChatOpenAI

# Global LLM instance
_llm: Optional[ChatOpenAI] = None


def get_llm() -> ChatOpenAI:
    """Get the configured LangChain LLM instance"""
    global _llm
    if _llm is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")

        _llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            model="openai/gpt-4o-mini",  # Good balance of performance and cost
            temperature=0.1,  # Low temperature for consistent, factual output
        )

    return _llm


def load_prompt_template(prompt_name: str) -> str:
    """Load a prompt template from the prompts directory"""
    prompt_path = Path(__file__).parent.parent / "prompts" / f"{prompt_name}.txt"
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise ValueError(f"Prompt template '{prompt_name}' not found at {prompt_path}")


# Import chains for easy access
from .cover_letter_chain import CoverLetterWriterChain
from .question_answer_chain import QuestionAnswerWriterChain

__all__ = [
    "get_llm",
    "load_prompt_template",
    "CoverLetterWriterChain",
    "QuestionAnswerWriterChain",
]
