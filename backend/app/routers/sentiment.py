"""
routers/sentiment.py
Fetches comments from the most-recent contest blog and runs NLP sentiment analysis.
"""
from __future__ import annotations

import re

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import db_models
from app.models.schemas import SentimentResponse
from app.services import cf_client, nlp_engine
from app.services.cf_client import validate_handle

router = APIRouter()

_NOT_AVAILABLE = lambda handle, **kw: SentimentResponse(
    handle=handle, available=False, **kw
)


def _strip_html(html: str) -> str:
    """Remove HTML tags from a string."""
    return re.sub(r"<[^>]+>", " ", html).strip()


async def _find_blog_entry_id(contest_name: str, contest_id: int) -> int | None:
    """
    Attempt to find a relevant blog entry for the given contest by:
    1. Fetching recent actions and matching contest name keywords.
    2. Returning None if nothing found.
    """
    try:
        actions = await cf_client.fetch_recent_actions(max_count=100)
    except Exception:
        return None

    # Keywords from the contest name for matching
    keywords = [w.lower() for w in contest_name.split() if len(w) > 3]

    for action in actions:
        entry = action.get("blogEntry")
        if not entry:
            continue
        title = (entry.get("title") or "").lower()
        # Match if the title contains ≥2 keywords from the contest name
        if sum(1 for kw in keywords if kw in title) >= 2:
            return entry.get("id")

    return None


@router.get("/{handle}", response_model=SentimentResponse)
async def get_sentiment(handle: str, db: Session = Depends(get_db)):
    """
    Find the most recent contest for the handle, look up its blog entry,
    fetch comments, and run VADER+TextBlob sentiment analysis.
    Returns available=False gracefully if any step fails.
    """
    handle = validate_handle(handle)

    # Get the most recent rating change to identify the latest contest
    latest_change = (
        db.query(db_models.CachedRatingChange)
        .filter_by(handle=handle)
        .order_by(db_models.CachedRatingChange.time_seconds.desc())
        .first()
    )

    if latest_change is None:
        return _NOT_AVAILABLE(handle)

    contest_name = latest_change.contest_name
    contest_id = latest_change.contest_id

    # Try to locate a blog entry for this contest
    blog_entry_id = await _find_blog_entry_id(contest_name, contest_id)

    if blog_entry_id is None:
        return _NOT_AVAILABLE(handle, contest_name=contest_name)

    # Fetch comments for that blog entry
    raw_comments = await cf_client.fetch_blog_comments(blog_entry_id)

    if not raw_comments:
        return _NOT_AVAILABLE(handle, contest_name=contest_name, blog_entry_id=blog_entry_id)

    # Extract text from the HTML field (most reliable)
    texts: list[str] = []
    for comment in raw_comments:
        html_text = comment.get("html") or comment.get("text") or ""
        cleaned = _strip_html(html_text)
        if cleaned:
            texts.append(cleaned)

    if not texts:
        return _NOT_AVAILABLE(handle, contest_name=contest_name, blog_entry_id=blog_entry_id)

    result = nlp_engine.analyze_comments(texts)

    return SentimentResponse(
        handle=handle,
        contest_name=contest_name,
        blog_entry_id=blog_entry_id,
        comment_count=result["comment_count"],
        compound_score=result["compound_score"],
        label=result["label"],
        available=True,
    )
