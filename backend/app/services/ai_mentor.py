"""AI Mentor service — Anthropic Claude integration for guidance and community assist."""

from __future__ import annotations


from collections.abc import AsyncGenerator

from app.core.config import settings

try:
    import anthropic

    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


MENTOR_SYSTEM_PROMPT = """You are CereForge AI Mentor, an expert AI engineering teacher. The user is working on a specific task and has a skill level of {skill_level}. Your role is to guide them toward understanding without giving away the answer. Adapt your language completely to their skill level: for absolute beginners use analogies and plain English with zero jargon; for engineers use precise technical language. When they ask about the task, ask them what they've tried so far first. Give hints progressively — don't dump all information at once. Be encouraging but honest. If they're wrong, explain why gently."""

COMMUNITY_SYSTEM_PROMPT = """You are an AI assistant analyzing a community Q&A discussion. Provide a concise summary of the question and existing answers, then add any important technical insights that were missed. Be precise. Format as: Summary | Key Points from Answers | Additional Insights | Recommended Next Steps. Stay within the domain of AI engineering."""


async def get_mentor_guidance(
    task_title: str,
    task_description: str,
    user_message: str,
    skill_level: str,
) -> AsyncGenerator[str, None]:
    """Stream AI mentor guidance for a task."""
    if not HAS_ANTHROPIC or not settings.ANTHROPIC_API_KEY:
        yield "AI Mentor is not configured. Please set the ANTHROPIC_API_KEY environment variable to enable this feature."
        return

    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    system_prompt = MENTOR_SYSTEM_PROMPT.format(skill_level=skill_level)
    context_message = f"The user is working on the task: '{task_title}'\n\nTask description: {task_description}\n\nUser's question: {user_message}"

    async with client.messages.stream(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": context_message}],
    ) as stream:
        async for text in stream.text_stream:
            yield text


async def get_community_assist(
    post_title: str,
    post_body: str,
    answers: list[str],
) -> AsyncGenerator[str, None]:
    """Stream AI analysis of a community Q&A discussion."""
    if not HAS_ANTHROPIC or not settings.ANTHROPIC_API_KEY:
        yield "AI analysis is not configured. Please set the ANTHROPIC_API_KEY environment variable."
        return

    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    answers_text = (
        "\n\n---\n\n".join([f"Answer {i+1}: {a}" for i, a in enumerate(answers)])
        if answers
        else "No answers yet."
    )

    context = f"Question: {post_title}\n\n{post_body}\n\nExisting Answers:\n{answers_text}"

    async with client.messages.stream(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        system=COMMUNITY_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": context}],
    ) as stream:
        async for text in stream.text_stream:
            yield text
