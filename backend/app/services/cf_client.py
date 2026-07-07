import re
import httpx
from fastapi import HTTPException
from app.config import settings

CF_API = settings.CF_API_BASE
TIMEOUT = 15.0


def validate_handle(handle: str) -> str:
    """
    Validate and clean a Codeforces handle.
    Rules: 3-24 chars, alphanumeric + underscore + hyphen only.
    Raises HTTPException(422) on failure.
    """
    handle = handle.strip()
    if len(handle) < 3 or len(handle) > 24:
        raise HTTPException(
            status_code=422,
            detail="Handle must be between 3 and 24 characters long.",
        )
    if not re.match(r"^[a-zA-Z0-9_\-]+$", handle):
        raise HTTPException(
            status_code=422,
            detail="Handle may only contain letters, digits, underscores, and hyphens.",
        )
    return handle


async def _get(url: str, params: dict) -> dict | list:
    """Make a GET request to the Codeforces API and handle common errors."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
        except httpx.TimeoutException:
            raise HTTPException(status_code=503, detail="Codeforces API timed out. Please try again.")
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Codeforces API returned HTTP {exc.response.status_code}.",
            )

    data = resp.json()
    if data.get("status") != "OK":
        comment = data.get("comment", "Unknown Codeforces API error.")
        comment_lower = comment.lower()
        if "not found" in comment_lower or "handles" in comment_lower or "handle" in comment_lower:
            raise HTTPException(status_code=404, detail=f"Codeforces handle not found: check the handle and try again.")
        raise HTTPException(status_code=400, detail=comment)
    return data["result"]


async def fetch_user_info(handle: str) -> dict:
    """Fetch user profile from Codeforces user.info endpoint."""
    result = await _get(CF_API + "user.info", {"handles": handle})
    return result[0]


async def fetch_rating_history(handle: str) -> list[dict]:
    """Fetch all rating changes for a user."""
    return await _get(CF_API + "user.rating", {"handle": handle})


async def fetch_submissions(handle: str, count: int = 1000) -> list[dict]:
    """Fetch recent submissions for a user (max 1000 without auth)."""
    return await _get(CF_API + "user.status", {"handle": handle, "count": count})


async def fetch_blog_comments(blog_entry_id: int) -> list[dict]:
    """Fetch comments for a blog entry. Returns empty list on any error."""
    try:
        result = await _get(CF_API + "blogEntry.comments", {"blogEntryId": blog_entry_id})
        return result if isinstance(result, list) else []
    except HTTPException:
        return []


async def fetch_recent_actions(max_count: int = 100) -> list[dict]:
    """Fetch recent actions on Codeforces (blog entries, comments, etc.)."""
    try:
        result = await _get(CF_API + "recentActions", {"maxCount": max_count})
        return result if isinstance(result, list) else []
    except HTTPException:
        return []
