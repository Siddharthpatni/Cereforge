"""Seed all 12 badges — idempotent."""

from __future__ import annotations

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
        "slug": "cereforge-elite",
        "name": "CereForge Elite",
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
    {
        "slug": "weekly-warrior",
        "name": "Weekly Warrior",
        "icon": "⚔️",
        "description": "You successfully completed a highly challenging Weekly Task.",
        "condition_type": "weekly_task",
        "condition_value": {"count": 1},
        "xp_bonus": 100,
        "display_order": 13,
    },
    # ─── NEW BADGES ────────────────────────────────────────────
    {
        "slug": "llm-specialist",
        "name": "LLM Specialist",
        "icon": "🔮",
        "description": "Completed 6 LLM tasks. You speak to machines fluently.",
        "condition_type": "track_count",
        "condition_value": {"track": "llm", "count": 6},
        "xp_bonus": 200,
        "display_order": 14,
    },
    {
        "slug": "rag-specialist",
        "name": "RAG Specialist",
        "icon": "🗄️",
        "description": "Completed 6 RAG tasks. You build AI with perfect memory.",
        "condition_type": "track_count",
        "condition_value": {"track": "rag", "count": 6},
        "xp_bonus": 200,
        "display_order": 15,
    },
    {
        "slug": "vision-specialist",
        "name": "Vision Specialist",
        "icon": "🦅",
        "description": "Completed 6 Vision tasks. You make machines perceive the world.",
        "condition_type": "track_count",
        "condition_value": {"track": "vision", "count": 6},
        "xp_bonus": 200,
        "display_order": 16,
    },
    {
        "slug": "agent-specialist",
        "name": "Agent Specialist",
        "icon": "🦾",
        "description": "Completed 6 Agent tasks. You build AI that acts autonomously.",
        "condition_type": "track_count",
        "condition_value": {"track": "agents", "count": 6},
        "xp_bonus": 200,
        "display_order": 17,
    },
    {
        "slug": "halfway-there",
        "name": "Halfway There",
        "icon": "⚡",
        "description": "Completed 12 total tasks. The journey to mastery is well underway.",
        "condition_type": "total_tasks",
        "condition_value": {"total_tasks": 12},
        "xp_bonus": 150,
        "display_order": 18,
    },
    {
        "slug": "expert-solver",
        "name": "Expert Solver",
        "icon": "💎",
        "description": "Submitted a solution to an Expert-difficulty task. Only the bold attempt these.",
        "condition_type": "difficulty_count",
        "condition_value": {"difficulty": "expert", "count": 1},
        "xp_bonus": 100,
        "display_order": 19,
    },
    {
        "slug": "community-mentor",
        "name": "Community Mentor",
        "icon": "🎓",
        "description": "Had 3 answers accepted by other members. You lift others up.",
        "condition_type": "accepted_answers",
        "condition_value": {"count": 3},
        "xp_bonus": 150,
        "display_order": 20,
    },
    {
        "slug": "knowledge-sharer",
        "name": "Knowledge Sharer",
        "icon": "📡",
        "description": "Posted 5 questions or answers in the CereForge community.",
        "condition_type": "post_count",
        "condition_value": {"count": 5},
        "xp_bonus": 50,
        "display_order": 21,
    },
    {
        "slug": "speed-runner",
        "name": "Speed Runner",
        "icon": "💨",
        "description": "Completed 3 tasks in a single day. You are relentlessly efficient.",
        "condition_type": "daily_tasks",
        "condition_value": {"count": 3},
        "xp_bonus": 75,
        "display_order": 22,
    },
    {
        "slug": "cereforge-legend",
        "name": "CereForge Legend",
        "icon": "🌟",
        "description": "All 24 tasks complete. You have conquered the full CereForge curriculum.",
        "condition_type": "total_tasks",
        "condition_value": {"total_tasks": 24},
        "xp_bonus": 1000,
        "display_order": 23,
    },
]


async def seed_badges(db: AsyncSession):
    """Seed all 23 badges — idempotent."""

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
