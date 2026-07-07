"""
analytics_engine.py
Pure functions for computing analytics from submission and rating-change data.
No I/O — all functions are unit-testable in isolation.
"""
from __future__ import annotations

import json
from collections import defaultdict

from app.models.schemas import (
    DifficultyBucket,
    RatingHistoryPoint,
    TagCount,
    VerdictCount,
    WeakTopic,
)

# Ordered difficulty buckets (lo, hi inclusive, label)
DIFFICULTY_BUCKETS: list[tuple[int, int, str]] = [
    (0,    1199, "<1200"),
    (1200, 1399, "1200-1399"),
    (1400, 1599, "1400-1599"),
    (1600, 1799, "1600-1799"),
    (1800, 1999, "1800-1999"),
    (2000, 2199, "2000-2199"),
    (2200, 2399, "2200-2399"),
    (2400, 9999, "2400+"),
]


def _parse_tags(tags_field) -> list[str]:
    """Parse tags from a JSON-encoded string or a plain Python list."""
    if isinstance(tags_field, list):
        return [str(t) for t in tags_field]
    if isinstance(tags_field, str):
        try:
            parsed = json.loads(tags_field)
            return [str(t) for t in parsed] if isinstance(parsed, list) else []
        except (json.JSONDecodeError, ValueError):
            return []
    return []


def _bucket_for_rating(rating: int) -> str:
    for lo, hi, label in DIFFICULTY_BUCKETS:
        if lo <= rating <= hi:
            return label
    return "2400+"


# ── Public API ────────────────────────────────────────────────────────────────

def solve_by_difficulty(submissions: list[dict]) -> list[DifficultyBucket]:
    """
    Count uniquely-accepted problems per difficulty bucket.
    Each problem is counted at most once (first AC wins).
    """
    seen: set[str] = set()
    counts: dict[str, int] = defaultdict(int)

    for s in submissions:
        if s.get("verdict") != "OK":
            continue
        key = s.get("problem_name", "")
        if key in seen:
            continue
        seen.add(key)
        rating = s.get("problem_rating")
        if rating is None:
            counts["Unrated"] += 1
        else:
            counts[_bucket_for_rating(int(rating))] += 1

    result: list[DifficultyBucket] = []
    for _, _, label in DIFFICULTY_BUCKETS:
        result.append(DifficultyBucket(bucket=label, count=counts.get(label, 0)))
    if counts.get("Unrated", 0):
        result.append(DifficultyBucket(bucket="Unrated", count=counts["Unrated"]))
    return result


def solve_by_tag(submissions: list[dict]) -> list[TagCount]:
    """
    Count uniquely-accepted problems per tag.
    Each problem is counted once per tag (not once per submission).
    """
    seen: set[str] = set()
    counts: dict[str, int] = defaultdict(int)

    for s in submissions:
        if s.get("verdict") != "OK":
            continue
        key = s.get("problem_name", "")
        if key in seen:
            continue
        seen.add(key)
        for tag in _parse_tags(s.get("tags", [])):
            if tag:
                counts[tag] += 1

    return sorted(
        [TagCount(tag=t, count=c) for t, c in counts.items()],
        key=lambda x: -x.count,
    )


def verdict_breakdown(submissions: list[dict]) -> list[VerdictCount]:
    """Count all submissions (including duplicates) per verdict type."""
    counts: dict[str, int] = defaultdict(int)
    for s in submissions:
        verdict = s.get("verdict") or "UNKNOWN"
        counts[verdict] += 1
    return sorted(
        [VerdictCount(verdict=v, count=c) for v, c in counts.items()],
        key=lambda x: -x.count,
    )


def weak_topics(submissions: list[dict], min_attempts: int = 3) -> list[WeakTopic]:
    """
    Identify tags where the user has a high attempt count but low accept rate.

    'attempts' = number of unique problems attempted for this tag
    'accepted' = number of unique problems accepted for this tag
    Only tags with attempts >= min_attempts are returned.
    Results are sorted by accept_rate ascending (worst first).
    """
    tag_problems: dict[str, set[str]] = defaultdict(set)
    tag_accepted: dict[str, set[str]] = defaultdict(set)

    for s in submissions:
        problem = s.get("problem_name", "")
        verdict = s.get("verdict")
        for tag in _parse_tags(s.get("tags", [])):
            if not tag:
                continue
            tag_problems[tag].add(problem)
            if verdict == "OK":
                tag_accepted[tag].add(problem)

    result: list[WeakTopic] = []
    for tag, problems in tag_problems.items():
        n_attempts = len(problems)
        if n_attempts < min_attempts:
            continue
        n_accepted = len(tag_accepted.get(tag, set()))
        rate = n_accepted / n_attempts if n_attempts > 0 else 0.0
        result.append(
            WeakTopic(
                tag=tag,
                attempts=n_attempts,
                accepted=n_accepted,
                accept_rate=round(rate, 3),
            )
        )

    # Sort: lowest accept_rate first; break ties by most attempts
    return sorted(result, key=lambda x: (x.accept_rate, -x.attempts))


def total_solved(submissions: list[dict]) -> int:
    """Count distinct problems with at least one Accepted submission."""
    return len({s["problem_name"] for s in submissions if s.get("verdict") == "OK"})


def rating_history_from_db(changes: list) -> list[RatingHistoryPoint]:
    """
    Convert a list of CachedRatingChange ORM objects to RatingHistoryPoint
    Pydantic models, sorted chronologically.
    """
    result: list[RatingHistoryPoint] = []
    for c in changes:
        result.append(
            RatingHistoryPoint(
                contest_id=c.contest_id,
                contest_name=c.contest_name,
                rank=c.rank or 0,
                old_rating=c.old_rating,
                new_rating=c.new_rating,
                time_seconds=c.time_seconds,
            )
        )
    return sorted(result, key=lambda x: x.time_seconds)
