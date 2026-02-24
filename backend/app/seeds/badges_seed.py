"""Seed all 12 badges — idempotent."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.badge import Badge


BADGES_DATA = [
    {
        "slug": "prompt-whisperer",
        "name": "Prompt Whisperer",
        "icon": "🧠",
        "description": "You completed your first LLM task. The neural pathway is open.",
        "condition_type": "track_count",
        "condition_value": {"track": "llm", "count": 1},
        "xp_bonus": 25,
        "display_order": 1,
    },
    {
        "slug": "chain-master",
        "name": "Chain Master",
        "icon": "🔗",
        "description": "You completed all LLM Engineering tasks. Master of language and logic.",
        "condition_type": "track_count",
        "condition_value": {"track": "llm", "count": 3},
        "xp_bonus": 100,
        "display_order": 2,
    },
    {
        "slug": "knowledge-architect",
        "name": "Knowledge Architect",
        "icon": "📚",
        "description": "You completed your first RAG task. You understand how AI finds knowledge.",
        "condition_type": "track_count",
        "condition_value": {"track": "rag", "count": 1},
        "xp_bonus": 25,
        "display_order": 3,
    },
    {
        "slug": "retrieval-expert",
        "name": "Retrieval Expert",
        "icon": "🎯",
        "description": "You mastered all RAG tasks. You can build AI with perfect recall.",
        "condition_type": "track_count",
        "condition_value": {"track": "rag", "count": 3},
        "xp_bonus": 100,
        "display_order": 4,
    },
    {
        "slug": "vision-forge",
        "name": "Vision Forge",
        "icon": "👁️",
        "description": "You completed your first Computer Vision task. Machines can see.",
        "condition_type": "track_count",
        "condition_value": {"track": "vision", "count": 1},
        "xp_bonus": 25,
        "display_order": 5,
    },
    {
        "slug": "sight-beyond-sight",
        "name": "Sight Beyond Sight",
        "icon": "🔭",
        "description": "You mastered all Computer Vision tasks. You make machines perceive reality.",
        "condition_type": "track_count",
        "condition_value": {"track": "vision", "count": 3},
        "xp_bonus": 100,
        "display_order": 6,
    },
    {
        "slug": "autonomy-unlocked",
        "name": "Autonomy Unlocked",
        "icon": "🤖",
        "description": "You completed your first Agent task. The age of autonomous AI begins.",
        "condition_type": "track_count",
        "condition_value": {"track": "agents", "count": 1},
        "xp_bonus": 25,
        "display_order": 7,
    },
    {
        "slug": "agent-overlord",
        "name": "Agent Overlord",
        "icon": "⚡",
        "description": "You mastered all Agent tasks. You architect AI that acts in the world.",
        "condition_type": "track_count",
        "condition_value": {"track": "agents", "count": 3},
        "xp_bonus": 100,
        "display_order": 8,
    },
    {
        "slug": "full-stack-ai",
        "name": "Full Stack AI",
        "icon": "🌐",
        "description": "One task in every track. You understand the full AI engineering stack.",
        "condition_type": "all_tracks",
        "condition_value": {"all_tracks": True},
        "xp_bonus": 150,
        "display_order": 9,
    },
    {
        "slug": "neuralforge-elite",
        "name": "NeuralForge Elite",
        "icon": "🏆",
        "description": "All 12 tasks complete. You are the embodiment of AI engineering mastery.",
        "condition_type": "total_tasks",
        "condition_value": {"total_tasks": 12},
        "xp_bonus": 500,
        "display_order": 10,
    },
    {
        "slug": "community-sage",
        "name": "Community Sage",
        "icon": "💬",
        "description": "Your answer was accepted as the best solution. The community trusts you.",
        "condition_type": "accepted_answers",
        "condition_value": {"count": 1},
        "xp_bonus": 75,
        "display_order": 11,
    },
    {
        "slug": "zero-to-ai",
        "name": "Zero to AI",
        "icon": "🚀",
        "description": "Started as a complete beginner and completed your first task. This is how legends begin.",
        "condition_type": "skill_and_tasks",
        "condition_value": {"skill_level": "absolute_beginner", "tasks_completed": 1},
        "xp_bonus": 50,
        "display_order": 12,
    },
]


async def seed_badges(db: AsyncSession):
    """Seed all 12 badges — idempotent."""
    for badge_data in BADGES_DATA:
        existing = await db.execute(select(Badge).where(Badge.slug == badge_data["slug"]))
        badge = existing.scalar_one_or_none()

        if badge:
            for key, value in badge_data.items():
                setattr(badge, key, value)
        else:
            badge = Badge(**badge_data)
            db.add(badge)

    await db.commit()
    print(f"✅ Seeded {len(BADGES_DATA)} badges")
