"""Seed community posts and comments."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User


async def seed_community(db: AsyncSession) -> None:
    print("Seeding community posts...")

    # Ensure cereforge_team user exists
    team_username = "cereforge_team"
    result = await db.execute(select(User).where(User.username == team_username))
    team_user = result.scalar_one_or_none()

    if not team_user:
        team_user = User(
            id=uuid.uuid4(),
            email="team@cereforge.io",
            username=team_username,
            password_hash=hash_password("TeamSecure123!"),
            is_active=True,
            is_admin=True,
            skill_level="advanced",
            xp=50000,
        )
        db.add(team_user)
        await db.flush()

    # Ensure admin@cereforge.io user exists
    admin_email = "admin@cereforge.io"
    result_admin = await db.execute(select(User).where(User.email == admin_email))
    admin_user = result_admin.scalar_one_or_none()

    if not admin_user:
        admin_user = User(
            id=uuid.uuid4(),
            email=admin_email,
            username="admin",
            password_hash=hash_password("AdminSecure123!"),
            is_active=True,
            is_admin=True,
            skill_level="advanced",
            xp=100000,
        )
        db.add(admin_user)
        await db.flush()

    # Pre-check existing posts so we are idempotent
    existing = await db.execute(select(Post.title))
    existing_titles = {t[0] for t in existing.all()}

    posts_data = [
        {
            "title": "How do I choose between RAG and fine-tuning for my use case?",
            "track": "rag",
            "tags": ["rag", "fine-tuning", "llm", "architecture"],
            "body": "I have a customer support dataset of 20,000 historical tickets and want to build an AI that can answer new tickets accurately. Should I fine-tune an LLM on this data or build a RAG system over it? What factors should push me toward one approach vs the other?",
            "status": "solved",
            "votes": 8,
            "answer": "use RAG when data changes frequently or you need source citations, use fine-tuning when you want consistent tone/style and data is stable. For support tickets RAG is usually better because new products and policies change the answers over time.",
            "is_beginner_friendly": False
        },
        {
            "title": "Getting hallucinations in my medical RAG — how to detect them?",
            "track": "rag",
            "tags": ["rag", "hallucination", "production", "medical"],
            "body": "My RAG pipeline for a medical knowledge base is occasionally returning answers that sound confident but are not supported by the retrieved documents. What is the best way to detect hallucinations before the answer reaches the user?",
            "status": "open",
            "votes": 2,
            "answer": None,
            "is_beginner_friendly": False
        },
        {
            "title": "LangChain vs LlamaIndex — which should I learn first?",
            "track": "agents",
            "tags": ["langchain", "llamaindex", "agents", "beginner"],
            "body": "I am starting to learn AI agent development and everyone recommends either LangChain or LlamaIndex. What are the real differences and which one should a beginner focus on?",
            "status": "solved",
            "votes": 5,
            "answer": "LangChain for agents and chains, LlamaIndex for document indexing and RAG. If you want to build agents start with LangChain. If your focus is document search start with LlamaIndex. Most production systems eventually use both.",
            "is_beginner_friendly": True
        },
        {
            "title": "YOLO vs Detectron2 for production object detection",
            "track": "vision",
            "tags": ["yolo", "computer-vision", "object-detection", "production"],
            "body": "Building a real-time defect detection system for a manufacturing line. Need to process 30 FPS at 1080p on an edge device. Should I use YOLOv8 or Detectron2? What are the tradeoffs?",
            "status": "open",
            "votes": 4,
            "answer": None,
            "is_beginner_friendly": False
        },
        {
            "title": "My vector similarity scores are all between 0.85 and 0.95 — is that normal?",
            "track": "rag",
            "tags": ["embeddings", "vector-search", "debugging"],
            "body": "I built my first RAG system and when I check the cosine similarity scores of retrieved chunks they all seem very high between 0.85 and 0.95 even for unrelated queries. I expected relevant chunks to score higher than irrelevant ones but the range is very narrow. Is this normal?",
            "status": "solved",
            "votes": 6,
            "answer": "this is normal with cosine similarity on dense embeddings. The absolute score is less meaningful than the relative ranking. Use the top-k retrieved by rank not by threshold. Consider switching to dot product similarity if using normalized embeddings for better spread.",
            "is_beginner_friendly": True
        },
        {
            "title": "How do multi-agent systems handle conflicting outputs from different agents?",
            "track": "agents",
            "tags": ["multi-agent", "langraph", "autonomous-agents"],
            "body": "I am building a multi-agent system with a Coder agent and a Reviewer agent. Sometimes the Reviewer rejects the Coder output 3 times in a row and the system gets stuck in a loop. How do production multi-agent systems handle this kind of deadlock?",
            "status": "open",
            "votes": 3,
            "answer": None,
            "is_beginner_friendly": False
        }
    ]

    for p_data in posts_data:
        if p_data["title"] in existing_titles:
            continue
            
        post = Post(
            id=uuid.uuid4(),
            author_id=team_user.id,
            title=p_data["title"],
            body=p_data["body"],
            track=p_data["track"],
            tags=p_data["tags"],
            status=p_data["status"],
            is_beginner_friendly=p_data["is_beginner_friendly"],
            vote_score=p_data["votes"]
        )
        db.add(post)
        await db.flush()
        
        # Add answer if any
        if p_data["answer"]:
            comment = Comment(
                id=uuid.uuid4(),
                post_id=post.id,
                author_id=team_user.id,
                body=p_data["answer"],
                is_accepted=True,
                vote_score=p_data["votes"] // 2
            )
            db.add(comment)
            await db.flush()
            
            post.accepted_answer_id = comment.id

    await db.commit()
    print("✅ Community seeded successfully!")
