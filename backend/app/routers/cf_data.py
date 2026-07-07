"""
routers/cf_data.py
Endpoints to fetch, cache, and refresh Codeforces user data.
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import db_models
from app.models.schemas import UserDataResponse, UserInfo
from app.services import cf_client

router = APIRouter()


def _user_to_schema(db_user: db_models.CachedUser) -> UserInfo:
    return UserInfo(
        handle=db_user.handle,
        rating=db_user.rating,
        max_rating=db_user.max_rating,
        rank=db_user.rank,
        max_rank=db_user.max_rank,
        avatar=db_user.avatar,
        country=db_user.country,
        city=db_user.city,
        organization=db_user.organization,
        contribution=db_user.contribution,
        registered_at=db_user.registered_at or 0,
    )


def _is_cache_fresh(db_user: db_models.CachedUser) -> bool:
    """Return True if the cached record is younger than CACHE_TTL_SECONDS."""
    fetched_at = db_user.fetched_at
    if fetched_at is None:
        return False
    # Make offset-naive datetime timezone-aware (SQLite stores UTC without tz)
    if fetched_at.tzinfo is None:
        fetched_at = fetched_at.replace(tzinfo=timezone.utc)
    age = datetime.now(timezone.utc) - fetched_at
    return age < timedelta(seconds=settings.CACHE_TTL_SECONDS)


async def _fetch_and_store(handle: str, db: Session) -> db_models.CachedUser:
    """Fetch all CF data concurrently and upsert into the database."""
    user_data, rating_history, submissions = await asyncio.gather(
        cf_client.fetch_user_info(handle),
        cf_client.fetch_rating_history(handle),
        cf_client.fetch_submissions(handle, count=1000),
    )

    # Upsert user
    db_user = db.query(db_models.CachedUser).filter_by(handle=handle).first()
    if db_user is None:
        db_user = db_models.CachedUser(handle=handle)
        db.add(db_user)

    db_user.rating = user_data.get("rating")
    db_user.max_rating = user_data.get("maxRating")
    db_user.rank = user_data.get("rank")
    db_user.max_rank = user_data.get("maxRank")
    db_user.avatar = user_data.get("avatar") or user_data.get("titlePhoto")
    db_user.country = user_data.get("country")
    db_user.city = user_data.get("city")
    db_user.organization = user_data.get("organization")
    db_user.contribution = user_data.get("contribution")
    db_user.registered_at = user_data.get("registrationTimeSeconds", 0)
    db_user.fetched_at = datetime.now(timezone.utc)

    # Replace submissions
    db.query(db_models.CachedSubmission).filter_by(handle=handle).delete()
    for sub in submissions:
        problem = sub.get("problem", {})
        tags = problem.get("tags", [])
        db.add(
            db_models.CachedSubmission(
                submission_id=sub.get("id", 0),
                handle=handle,
                verdict=sub.get("verdict"),
                problem_name=problem.get("name", "Unknown"),
                problem_rating=problem.get("rating"),
                tags=json.dumps(tags),
                language=sub.get("programmingLanguage"),
                time_seconds=sub.get("creationTimeSeconds", 0),
            )
        )

    # Replace rating changes
    db.query(db_models.CachedRatingChange).filter_by(handle=handle).delete()
    for change in rating_history:
        db.add(
            db_models.CachedRatingChange(
                handle=handle,
                contest_id=change.get("contestId", 0),
                contest_name=change.get("contestName", "Unknown Contest"),
                rank=change.get("rank"),
                old_rating=change.get("oldRating", 0),
                new_rating=change.get("newRating", 0),
                time_seconds=change.get("ratingUpdateTimeSeconds", 0),
            )
        )

    db.commit()
    db.refresh(db_user)
    return db_user


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/user/{handle}", response_model=UserDataResponse)
async def get_user(handle: str, db: Session = Depends(get_db)):
    """
    Fetch (or return cached) Codeforces user data.
    Cache is considered fresh for CACHE_TTL_SECONDS (default 1 hour).
    """
    handle = cf_client.validate_handle(handle)

    db_user = db.query(db_models.CachedUser).filter_by(handle=handle).first()

    if db_user and _is_cache_fresh(db_user):
        return UserDataResponse(
            user=_user_to_schema(db_user),
            cached=True,
            fetched_at=db_user.fetched_at.isoformat(),
        )

    # Cache miss or stale — fetch from Codeforces API
    db_user = await _fetch_and_store(handle, db)

    return UserDataResponse(
        user=_user_to_schema(db_user),
        cached=False,
        fetched_at=db_user.fetched_at.isoformat(),
    )


@router.delete("/user/{handle}")
async def clear_cache(handle: str, db: Session = Depends(get_db)):
    """Delete all cached data for a Codeforces handle (force refresh)."""
    handle = cf_client.validate_handle(handle)

    db_user = db.query(db_models.CachedUser).filter_by(handle=handle).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail=f"No cached data for handle '{handle}'.")

    db.delete(db_user)
    db.commit()
    return {"message": f"Cache cleared for '{handle}'."}
