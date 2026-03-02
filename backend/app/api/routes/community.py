"""Community routes: posts CRUD, comments, voting, AI assist."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.comment import Comment, Vote
from app.models.post import Post
from app.models.task import Task
from app.models.user import User
from app.schemas.post import (
    AuthorResponse,
    CommentCreate,
    PostCreate,
    PostListItem,
    PostListResponse,
    PostResponse,
    PostUpdate,
    VoteCreate,
    VoteResponse,
)
from app.services.badge_engine import check_and_award_badges
from app.services.notification import create_notification
from app.services.xp_service import (
    XP_ANSWER_ACCEPTED,
    XP_ANSWER_POSTED,
    XP_COMMENT_UPVOTED,
    XP_POST_UPVOTED,
    award_xp,
)

router = APIRouter()
vote_router = APIRouter()
ai_router = APIRouter()


@router.get("", response_model=PostListResponse)
async def list_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_current_user)] = None,
    track: str | None = Query(None),
    tag: str | None = Query(None),
    post_status: str | None = Query(None, alias="status"),
    sort: str | None = Query("newest"),
    beginner_friendly: bool | None = Query(None),
    search: str | None = Query(None),
    bookmarked_only: bool = Query(False),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """List community posts with filters, sorting, and pagination."""
    from app.models.post import PostBookmark

    query = select(Post).where(Post.is_deleted.is_(False))

    if track:
        query = query.where(Post.track == track)
    if tag:
        query = query.where(Post.tags.any(tag))  # type: ignore
    if post_status:
        query = query.where(Post.status == post_status)
    if beginner_friendly:
        query = query.where(Post.is_beginner_friendly)
    if search:
        query = query.where(
            or_(
                Post.title.ilike(f"%{search}%"),
                Post.body.ilike(f"%{search}%"),
            )
        )

    if bookmarked_only and current_user:
        query = query.join(PostBookmark, Post.id == PostBookmark.post_id).where(
            PostBookmark.user_id == current_user.id
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Sort
    if sort == "votes":
        query = query.order_by(desc(Post.vote_score))
    elif sort == "unanswered":
        query = query.where(Post.status == "open").order_by(desc(Post.created_at))
    else:
        query = query.order_by(desc(Post.created_at))

    # Paginate
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    posts = result.scalars().all()

    # Pre-fetch bookmarks for fast resolution
    bookmarked_post_ids = set()
    if current_user and posts:
        b_result = await db.execute(
            select(PostBookmark.post_id).where(
                PostBookmark.user_id == current_user.id,
                PostBookmark.post_id.in_([p.id for p in posts]),
            )
        )
        bookmarked_post_ids = set(b_result.scalars().all())

    items = []
    for post in posts:
        # Count comments
        comment_count_result = await db.execute(
            select(func.count(Comment.id)).where(
                Comment.post_id == post.id, Comment.is_deleted.is_(False)
            )
        )
        comment_count = comment_count_result.scalar() or 0

        items.append(
            PostListItem(
                id=post.id,
                author=AuthorResponse.model_validate(post.author),
                title=post.title,
                body=post.body[:200] + "..." if len(post.body) > 200 else post.body,
                track=post.track,
                tags=post.tags or [],
                colab_link=post.colab_link,
                status=post.status,
                vote_score=post.vote_score,
                view_count=post.view_count,
                is_beginner_friendly=post.is_beginner_friendly,
                comment_count=comment_count,
                is_bookmarked=(post.id in bookmarked_post_ids),
                created_at=post.created_at,
            )
        )

    pages = (total + limit - 1) // limit

    return PostListResponse(items=items, total=total, page=page, pages=pages)


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: PostCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Create a new community post."""
    post = Post(
        author_id=current_user.id,
        title=data.title,
        body=data.body,
        track=data.track,
        tags=data.tags,
        colab_link=data.colab_link,
        related_task_id=data.related_task_id,
        is_beginner_friendly=data.is_beginner_friendly,
    )
    db.add(post)
    await db.flush()
    await db.commit()

    await db.refresh(post)
    await db.refresh(post, ["author"])
    return {"post": PostResponse.model_validate(post).model_dump()}


@router.get("/{post_id}", response_model=dict)
async def get_post(
    post_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get a single post with threaded comments."""
    from sqlalchemy.orm import joinedload, noload

    result = await db.execute(
        select(Post)
        .options(joinedload(Post.author))
        .where(Post.id == post_id, Post.is_deleted.is_(False))
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    # Increment view count
    post.view_count += 1
    await db.flush()

    # Get all comments for the post at once to avoid lazy-loading issues (MissingGreenletError)
    comments_result = await db.execute(
        select(Comment)
        .options(joinedload(Comment.author), noload(Comment.replies), noload(Comment.parent))
        .where(Comment.post_id == post_id, Comment.is_deleted.is_(False))
        .order_by(desc(Comment.is_accepted), desc(Comment.vote_score), Comment.created_at)
    )
    all_comments = comments_result.scalars().unique().all()

    # Group comments by parent_id
    from collections import defaultdict

    children_map = defaultdict(list)
    for c in all_comments:
        children_map[c.parent_id].append(c)

    def build_comment_tree(comment: Comment) -> dict:
        return {
            "id": str(comment.id),
            "post_id": str(comment.post_id),
            "author": AuthorResponse.model_validate(comment.author).model_dump(),
            "parent_id": str(comment.parent_id) if comment.parent_id else None,
            "body": comment.body,
            "vote_score": comment.vote_score,
            "is_accepted": comment.is_accepted,
            "created_at": comment.created_at.isoformat(),
            "updated_at": comment.updated_at.isoformat(),
            "replies": [build_comment_tree(r) for r in children_map[comment.id]],
        }

    # Start tree from top-level comments
    comments_data = [build_comment_tree(c) for c in children_map[None]]

    # Check bookmark status
    from app.models.post import PostBookmark

    is_bookmarked = False
    if current_user:
        b_result = await db.execute(
            select(PostBookmark).where(
                PostBookmark.user_id == current_user.id, PostBookmark.post_id == post.id
            )
        )
        if b_result.scalar_one_or_none():
            is_bookmarked = True

    await db.commit()

    post_resp = PostResponse.model_validate(post)
    post_resp.is_bookmarked = is_bookmarked

    return {
        "post": post_resp.model_dump(),
        "comments": comments_data,
    }


@router.patch("/{post_id}", response_model=dict)
async def update_post(
    post_id: UUID,
    data: PostUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Update a post (author only)."""
    result = await db.execute(select(Post).where(Post.id == post_id, Post.is_deleted.is_(False)))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the post author")

    if data.title is not None:
        post.title = data.title
    if data.body is not None:
        post.body = data.body

    await db.flush()
    await db.commit()
    return {"post": PostResponse.model_validate(post).model_dump()}


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Delete a post (author or admin)."""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    post.is_deleted = True
    await db.flush()
    await db.commit()


@router.post("/{post_id}/bookmark", response_model=dict)
async def toggle_bookmark(
    post_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Toggle a bookmark/favorite on a community post."""
    from app.models.post import PostBookmark

    # Verify post exists
    post_result = await db.execute(
        select(Post).where(Post.id == post_id, Post.is_deleted.is_(False))
    )
    if not post_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    # Check if already bookmarked
    b_result = await db.execute(
        select(PostBookmark).where(
            PostBookmark.user_id == current_user.id, PostBookmark.post_id == post_id
        )
    )
    bookmark = b_result.scalar_one_or_none()

    if bookmark:
        await db.delete(bookmark)
        await db.commit()
        return {"bookmarked": False}
    else:
        new_bookmark = PostBookmark(user_id=current_user.id, post_id=post_id)
        db.add(new_bookmark)
        await db.commit()
        return {"bookmarked": True}
    return None


@router.post("/{post_id}/comments", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: UUID,
    data: CommentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Add a comment (answer or reply) to a post."""
    result = await db.execute(select(Post).where(Post.id == post_id, Post.is_deleted.is_(False)))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    comment = Comment(
        post_id=post_id,
        author_id=current_user.id,
        parent_id=data.parent_id,
        body=data.body,
    )
    db.add(comment)

    # Award XP for answering
    await award_xp(db, current_user.id, XP_ANSWER_POSTED)

    await db.flush()
    await db.commit()
    await db.refresh(comment, ["author"])

    return {
        "comment": {
            "id": str(comment.id),
            "post_id": str(comment.post_id),
            "author": AuthorResponse.model_validate(comment.author).model_dump(),
            "parent_id": str(comment.parent_id) if comment.parent_id else None,
            "body": comment.body,
            "vote_score": comment.vote_score,
            "is_accepted": comment.is_accepted,
            "created_at": comment.created_at.isoformat(),
            "updated_at": comment.updated_at.isoformat(),
            "replies": [],
        }
    }


@router.post("/{post_id}/comments/{comment_id}/accept", response_model=dict)
async def accept_answer(
    post_id: UUID,
    comment_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Accept a comment as the answer (post author only)."""
    post_result = await db.execute(
        select(Post).where(Post.id == post_id, Post.is_deleted.is_(False))
    )
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only the post author can accept answers"
        )
    if post.status != "open":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post is not open")

    comment_result = await db.execute(
        select(Comment).where(Comment.id == comment_id, Comment.post_id == post_id)
    )
    comment = comment_result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    # Mark as accepted
    comment.is_accepted = True
    post.status = "solved"
    post.accepted_answer_id = comment_id

    # Award XP to comment author
    await award_xp(db, comment.author_id, XP_ANSWER_ACCEPTED)

    # Create notification for comment author
    await create_notification(
        db,
        comment.author_id,
        type="answer_accepted",
        title="Your answer was accepted! 🎉",
        body=f'Your answer on "{post.title}" was marked as the accepted solution.',
        metadata={"post_id": str(post_id), "comment_id": str(comment_id)},
    )

    # Check badges for the comment author
    newly_earned = await check_and_award_badges(db, comment.author_id)

    await db.flush()
    await db.commit()

    return {
        "comment": {
            "id": str(comment.id),
            "is_accepted": True,
        },
        "newly_earned_badges": newly_earned,
    }


@vote_router.post("/vote", response_model=VoteResponse)
async def vote(
    data: VoteCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Vote on a post or comment (+1 or -1)."""
    # Get target and check ownership
    if data.target_type == "post":
        target_result = await db.execute(select(Post).where(Post.id == data.target_id))
        target = target_result.scalar_one_or_none()
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        if target.author_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot vote on your own post"
            )
    else:
        target_result = await db.execute(select(Comment).where(Comment.id == data.target_id))
        target = target_result.scalar_one_or_none()
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        if target.author_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot vote on your own comment"
            )

    # Check existing vote
    existing_result = await db.execute(
        select(Vote).where(
            Vote.user_id == current_user.id,
            Vote.target_id == data.target_id,
            Vote.target_type == data.target_type,
        )
    )
    existing_vote = existing_result.scalar_one_or_none()

    if existing_vote:
        if existing_vote.value == data.value:
            # Undo vote
            target.vote_score -= existing_vote.value
            await db.delete(existing_vote)
            await db.flush()
            await db.commit()
            return VoteResponse(new_score=target.vote_score, user_vote=0)
        else:
            # Change vote direction
            target.vote_score -= existing_vote.value
            target.vote_score += data.value
            existing_vote.value = data.value
    else:
        # New vote
        new_vote = Vote(
            user_id=current_user.id,
            target_id=data.target_id,
            target_type=data.target_type,
            value=data.value,
        )
        db.add(new_vote)
        target.vote_score += data.value

        # Award XP for upvotes (XP is never removed)
        if data.value == 1:
            xp_amount = XP_POST_UPVOTED if data.target_type == "post" else XP_COMMENT_UPVOTED
            await award_xp(db, target.author_id, xp_amount)

    await db.flush()
    await db.commit()

    return VoteResponse(new_score=target.vote_score, user_vote=data.value)


@ai_router.post("/ai-mentor/guidance")
async def ai_mentor_guidance(
    data: dict,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get AI mentor guidance for a specific task (streamed)."""
    from app.services.ai_mentor import get_mentor_guidance

    task_slug = data.get("task_slug", "")
    user_message = data.get("user_message", "")

    task_result = await db.execute(select(Task).where(Task.slug == task_slug))
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return StreamingResponse(
        get_mentor_guidance(
            task_title=task.title,
            task_description=task.description,
            user_message=user_message,
            skill_level=current_user.skill_level,
        ),
        media_type="text/event-stream",
    )


@ai_router.post("/ai-mentor/community-assist")
async def ai_community_assist(
    data: dict,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get AI analysis of a community Q&A discussion (streamed)."""
    from app.services.ai_mentor import get_community_assist

    post_id = data.get("post_id")
    if not post_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="post_id required")

    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    comments_result = await db.execute(
        select(Comment).where(
            Comment.post_id == post_id, Comment.is_deleted.is_(False), Comment.parent_id.is_(None)
        )
    )
    answers = [c.body for c in comments_result.scalars().all()]

    return StreamingResponse(
        get_community_assist(
            post_title=post.title,
            post_body=post.body,
            answers=answers,
        ),
        media_type="text/event-stream",
    )
