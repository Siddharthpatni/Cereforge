"""Seed all 3 learning paths with modules and lessons — idempotent."""

from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learning_path import LearningPath, PathLesson, PathModule
from app.models.task import Task

PATHS_DATA = [
    {
        "slug": "zero-to-ai-path",
        "title": "Zero to AI — Complete Beginner Path",
        "description": (
            "Never written a line of AI code? Never heard of embeddings or transformers? Perfect starting point. "
            "We start with plain English concepts and no-code exercises, then gradually introduce technical thinking. "
            "By Day 30, you'll understand how AI systems are built well enough to discuss them with any AI engineer."
        ),
        "for_skill_levels": ["absolute_beginner", "some_python"],
        "duration_days": 30,
        "task_slugs": [
            "llm-prompt-chain",
            "llm-token-optimizer",
            "rag-intro-flow",
            "cv-real-world-survey",
            "agent-fundamentals",
        ],
        "display_order": 1,
        "modules": [
            {
                "title": "AI Fundamentals (Days 1-7)",
                "display_order": 1,
                "lessons": [
                    {
                        "title": "What is an LLM? No math, no jargon",
                        "lesson_type": "article",
                        "duration_minutes": 15,
                        "display_order": 1,
                    },
                    {
                        "title": "Your first conversation with an API",
                        "lesson_type": "colab",
                        "duration_minutes": 30,
                        "display_order": 2,
                    },
                    {
                        "title": "Prompt Engineering Basics — 5 patterns that always work",
                        "lesson_type": "article",
                        "duration_minutes": 20,
                        "display_order": 3,
                    },
                ],
            },
            {
                "title": "RAG and Memory (Days 8-16)",
                "display_order": 2,
                "lessons": [
                    {
                        "title": "What are Embeddings? The intuition",
                        "lesson_type": "article",
                        "duration_minutes": 20,
                        "display_order": 1,
                    },
                    {
                        "title": "Building a simple RAG with 30 lines",
                        "lesson_type": "colab",
                        "duration_minutes": 45,
                        "display_order": 2,
                    },
                    {
                        "title": "When to use RAG vs Fine-tuning",
                        "lesson_type": "article",
                        "duration_minutes": 15,
                        "display_order": 3,
                    },
                ],
            },
            {
                "title": "Vision and Agents (Days 17-30)",
                "display_order": 3,
                "lessons": [
                    {
                        "title": "Computer Vision in 15 minutes",
                        "lesson_type": "video",
                        "duration_minutes": 15,
                        "display_order": 1,
                    },
                    {
                        "title": "What is an AI Agent? With real examples",
                        "lesson_type": "article",
                        "duration_minutes": 20,
                        "display_order": 2,
                    },
                    {
                        "title": "Your first LangChain agent",
                        "lesson_type": "colab",
                        "duration_minutes": 60,
                        "display_order": 3,
                    },
                ],
            },
        ],
    },
    {
        "slug": "production-rag-path",
        "title": "Production RAG Systems",
        "description": (
            "You know the basics of machine learning. This path takes you from RAG prototype to production-grade system. "
            "You'll learn chunking strategies, vector database architecture, hybrid search, hallucination prevention, "
            "and how to evaluate RAG quality."
        ),
        "for_skill_levels": ["ml_familiar", "advanced"],
        "duration_days": 21,
        "task_slugs": ["rag-intro-flow", "rag-vector-architect", "rag-hallucination-guard"],
        "display_order": 2,
        "modules": [
            {
                "title": "Advanced Retrieval",
                "display_order": 1,
                "lessons": [
                    {
                        "title": "Semantic vs Fixed-Size Chunking — when each works",
                        "lesson_type": "article",
                        "duration_minutes": 25,
                        "display_order": 1,
                    },
                    {
                        "title": "Hierarchical indexing for long documents",
                        "lesson_type": "colab",
                        "duration_minutes": 60,
                        "display_order": 2,
                    },
                    {
                        "title": "Hybrid search — combining dense and sparse retrieval",
                        "lesson_type": "article",
                        "duration_minutes": 30,
                        "display_order": 3,
                    },
                ],
            },
            {
                "title": "Production Hardening",
                "display_order": 2,
                "lessons": [
                    {
                        "title": "RAGAS — automated RAG evaluation",
                        "lesson_type": "colab",
                        "duration_minutes": 45,
                        "display_order": 1,
                    },
                    {
                        "title": "Monitoring RAG in production — what metrics matter",
                        "lesson_type": "article",
                        "duration_minutes": 20,
                        "display_order": 2,
                    },
                ],
            },
        ],
    },
    {
        "slug": "agents-masterclass-path",
        "title": "Autonomous AI Agents Masterclass",
        "description": (
            "From ReAct to LangGraph to multi-agent orchestration. Build production-ready AI agents that reason, "
            "plan, use tools, and recover from failures."
        ),
        "for_skill_levels": ["ml_familiar", "advanced"],
        "duration_days": 28,
        "task_slugs": [
            "agent-fundamentals",
            "agent-langchain-research",
            "agent-multi-agent-system",
        ],
        "display_order": 3,
        "modules": [
            {
                "title": "Agent Architecture Patterns",
                "display_order": 1,
                "lessons": [
                    {
                        "title": "ReAct, CoT, and Tree-of-Thought — which and when",
                        "lesson_type": "article",
                        "duration_minutes": 30,
                        "display_order": 1,
                    },
                    {
                        "title": "Tool-calling with function calling APIs",
                        "lesson_type": "colab",
                        "duration_minutes": 45,
                        "display_order": 2,
                    },
                    {
                        "title": "LangGraph stateful agent flows",
                        "lesson_type": "colab",
                        "duration_minutes": 90,
                        "display_order": 3,
                    },
                ],
            },
            {
                "title": "Multi-Agent Systems",
                "display_order": 2,
                "lessons": [
                    {
                        "title": "Designing agent communication protocols",
                        "lesson_type": "article",
                        "duration_minutes": 25,
                        "display_order": 1,
                    },
                    {
                        "title": "Human-in-the-loop checkpoints — when and how",
                        "lesson_type": "article",
                        "duration_minutes": 20,
                        "display_order": 2,
                    },
                    {
                        "title": "Cost optimization for multi-agent systems",
                        "lesson_type": "article",
                        "duration_minutes": 20,
                        "display_order": 3,
                    },
                ],
            },
        ],
    },
]


async def seed_paths(db: AsyncSession):
    """Seed all 3 learning paths with modules and lessons — idempotent."""
    for path_data in PATHS_DATA:
        task_slugs = cast(list[str], path_data.pop("task_slugs"))
        modules_data = cast(list[dict[str, Any]], path_data.pop("modules"))

        # Resolve task slugs to IDs
        task_ids = []
        for slug in task_slugs:
            result = await db.execute(select(Task.id).where(Task.slug == slug))
            task_id = result.scalar_one_or_none()
            if task_id:
                task_ids.append(task_id)

        path_data["task_sequence"] = task_ids

        # Upsert path
        existing = await db.execute(
            select(LearningPath).where(LearningPath.slug == path_data["slug"])
        )
        path = existing.scalar_one_or_none()

        if path:
            for key, value in path_data.items():
                setattr(path, key, value)
        else:
            path = LearningPath(**path_data)
            db.add(path)

        await db.flush()

        # Upsert modules and lessons
        for module_data in modules_data:  # type: ignore
            lessons_data = module_data.pop("lessons", [])

            existing_mod = await db.execute(
                select(PathModule).where(
                    PathModule.path_id == path.id,
                    PathModule.title == module_data["title"],
                )
            )
            module = existing_mod.scalar_one_or_none()
            if module:
                module.display_order = module_data["display_order"]
            else:
                module = PathModule(path_id=path.id, **module_data)
                db.add(module)

            await db.flush()

            for lesson_data in lessons_data:  # type: ignore
                existing_lesson = await db.execute(
                    select(PathLesson).where(
                        PathLesson.module_id == module.id,
                        PathLesson.title == lesson_data["title"],
                    )
                )
                lesson = existing_lesson.scalar_one_or_none()
                if lesson:
                    for key, value in lesson_data.items():
                        setattr(lesson, key, value)
                else:
                    lesson = PathLesson(module_id=module.id, **lesson_data)
                    db.add(lesson)

    await db.commit()
    print(f"✅ Seeded {len(PATHS_DATA)} learning paths with modules and lessons")
