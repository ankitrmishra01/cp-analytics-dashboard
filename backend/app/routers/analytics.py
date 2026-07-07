"""
routers/analytics.py
Compute and return analytics from cached submission + rating data.
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import db_models
from app.models.schemas import AnalyticsResponse
from app.services import analytics_engine
from app.services.cf_client import validate_handle

router = APIRouter()


def _submission_to_dict(sub: db_models.CachedSubmission) -> dict:
    """Convert ORM submission to dict with tags as a Python list."""
    tags = []
    if sub.tags:
        try:
            tags = json.loads(sub.tags)
        except (json.JSONDecodeError, ValueError):
            tags = []
    return {
        "submission_id": sub.submission_id,
        "verdict": sub.verdict,
        "problem_name": sub.problem_name,
        "problem_rating": sub.problem_rating,
        "tags": tags,
        "language": sub.language,
        "time_seconds": sub.time_seconds,
    }


@router.get("/{handle}", response_model=AnalyticsResponse)
def get_analytics(handle: str, db: Session = Depends(get_db)):
    """
    Return computed analytics for a cached Codeforces handle.
    The handle must have been fetched first via GET /api/cf/user/{handle}.
    """
    handle = validate_handle(handle)

    db_user = db.query(db_models.CachedUser).filter_by(handle=handle).first()
    if db_user is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No data found for handle '{handle}'. "
                "Please fetch the user first via GET /api/cf/user/{handle}."
            ),
        )

    submissions = [
        _submission_to_dict(s)
        for s in db.query(db_models.CachedSubmission).filter_by(handle=handle).all()
    ]
    rating_changes = (
        db.query(db_models.CachedRatingChange)
        .filter_by(handle=handle)
        .all()
    )

    return AnalyticsResponse(
        handle=handle,
        rating_history=analytics_engine.rating_history_from_db(rating_changes),
        difficulty_distribution=analytics_engine.solve_by_difficulty(submissions),
        tag_distribution=analytics_engine.solve_by_tag(submissions),
        verdict_distribution=analytics_engine.verdict_breakdown(submissions),
        weak_topics=analytics_engine.weak_topics(submissions, min_attempts=3),
        total_solved=analytics_engine.total_solved(submissions),
        total_submissions=len(submissions),
    )
