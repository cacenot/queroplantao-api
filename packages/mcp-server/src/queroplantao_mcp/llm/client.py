"""
LLM client wrapper for analysis tools.

Provides a simple interface for calling OpenAI models for code analysis
and business rule explanations.
"""

from __future__ import annotations

import logging

from openai import AsyncOpenAI

from queroplantao_mcp.config import (
    LLM_MAX_TOKENS,
    LLM_MODEL,
    LLM_TEMPERATURE,
    OPENAI_API_KEY,
)

logger = logging.getLogger(__name__)


class LLMClient:
    """Async client for LLM interactions."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        self._api_key = api_key or OPENAI_API_KEY
        self._model = model or LLM_MODEL
        self._temperature = temperature if temperature is not None else LLM_TEMPERATURE
        self._max_tokens = max_tokens or LLM_MAX_TOKENS
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI:
        """Get or create the OpenAI client."""
        if self._client is None:
            if not self._api_key:
                raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")
            self._client = AsyncOpenAI(api_key=self._api_key)
        return self._client

    async def chat(
        self,
        user_message: str,
        system_message: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Send a chat message and get a response.

        Args:
            user_message: The user's message/question.
            system_message: Optional system prompt.
            temperature: Override default temperature.
            max_tokens: Override default max tokens.

        Returns:
            The assistant's response text.
        """
        client = self._get_client()

        messages: list[dict[str, str]] = []

        if system_message:
            messages.append({"role": "system", "content": system_message})

        messages.append({"role": "user", "content": user_message})

        try:
            response = await client.chat.completions.create(
                model=self._model,
                messages=messages,  # type: ignore
                temperature=temperature if temperature is not None else self._temperature,
                max_tokens=max_tokens or self._max_tokens,
            )

            content = response.choices[0].message.content
            return content or ""

        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            raise

    async def analyze_code(
        self,
        code: str,
        question: str,
        context: str | None = None,
    ) -> str:
        """
        Analyze code with a specific question.

        Args:
            code: The code to analyze.
            question: What to analyze about the code.
            context: Additional context about the codebase.

        Returns:
            Analysis result.
        """
        from queroplantao_mcp.llm.prompts import CODE_ANALYSIS_SYSTEM_PROMPT

        user_message = f"""## Code to Analyze

```python
{code}
```

## Question

{question}
"""

        if context:
            user_message += f"""
## Additional Context

{context}
"""

        return await self.chat(
            user_message=user_message,
            system_message=CODE_ANALYSIS_SYSTEM_PROMPT,
        )

    async def explain_business_rule(
        self,
        topic: str,
        related_code: str | None = None,
        documentation: str | None = None,
    ) -> str:
        """
        Explain a business rule.

        Args:
            topic: The topic/rule to explain.
            related_code: Related code snippets.
            documentation: Related documentation.

        Returns:
            Explanation of the business rule.
        """
        from queroplantao_mcp.llm.prompts import BUSINESS_RULE_SYSTEM_PROMPT

        user_message = f"""## Topic

{topic}
"""

        if documentation:
            user_message += f"""
## Related Documentation

{documentation}
"""

        if related_code:
            user_message += f"""
## Related Code

```python
{related_code}
```
"""

        return await self.chat(
            user_message=user_message,
            system_message=BUSINESS_RULE_SYSTEM_PROMPT,
        )

    async def generate_diagram(
        self,
        workflow: str,
        format_: str = "mermaid",
        context: str | None = None,
    ) -> str:
        """
        Generate a workflow diagram.

        Args:
            workflow: Description of the workflow.
            format_: Diagram format (mermaid, ascii).
            context: Additional context.

        Returns:
            Diagram in the specified format.
        """
        from queroplantao_mcp.llm.prompts import DIAGRAM_SYSTEM_PROMPT

        user_message = f"""## Workflow

{workflow}

## Output Format

Generate a {format_} diagram.
"""

        if context:
            user_message += f"""
## Context

{context}
"""

        return await self.chat(
            user_message=user_message,
            system_message=DIAGRAM_SYSTEM_PROMPT,
        )


# Singleton instance
_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Get the singleton LLM client instance."""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
