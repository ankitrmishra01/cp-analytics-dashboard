from __future__ import annotations
from pydantic import BaseModel


# ── User Info ─────────────────────────────────────────────────────────────────

class UserInfo(BaseModel):
    handle: str
    rating: int | None = None
    max_rating: int | None = None
    rank: str | None = None
    max_rank: str | None = None
    avatar: str | None = None
    country: str | None = None
    city: str | None = None
    organization: str | None = None
    contribution: int | None = None
    registered_at: int = 0


class UserDataResponse(BaseModel):
    user: UserInfo
    cached: bool
    fetched_at: str


# ── Analytics ─────────────────────────────────────────────────────────────────

class RatingHistoryPoint(BaseModel):
    contest_id: int
    contest_name: str
    rank: int
    old_rating: int
    new_rating: int
    time_seconds: int


class DifficultyBucket(BaseModel):
    bucket: str
    count: int


class TagCount(BaseModel):
    tag: str
    count: int


class VerdictCount(BaseModel):
    verdict: str
    count: int


class WeakTopic(BaseModel):
    tag: str
    attempts: int
    accepted: int
    accept_rate: float


class AnalyticsResponse(BaseModel):
    handle: str
    rating_history: list[RatingHistoryPoint]
    difficulty_distribution: list[DifficultyBucket]
    tag_distribution: list[TagCount]
    verdict_distribution: list[VerdictCount]
    weak_topics: list[WeakTopic]
    total_solved: int
    total_submissions: int


# ── Sentiment ─────────────────────────────────────────────────────────────────

class SentimentResponse(BaseModel):
    handle: str
    contest_name: str | None = None
    blog_entry_id: int | None = None
    comment_count: int = 0
    compound_score: float = 0.0
    label: str = "neutral"   # "positive" | "neutral" | "negative"
    available: bool = False
