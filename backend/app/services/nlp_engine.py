"""
nlp_engine.py
Sentiment analysis pipeline using VADER (primary) and TextBlob (secondary).
"""
from __future__ import annotations

import re

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

_vader = SentimentIntensityAnalyzer()

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def _clean_text(text: str) -> str:
    """Strip HTML tags and collapse whitespace."""
    text = _HTML_TAG_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def analyze_comments(comments: list[str]) -> dict:
    """
    Run sentiment analysis on a list of comment strings.

    Strategy:
    - VADER compound score (primary, weight 0.70)
    - TextBlob polarity (secondary, weight 0.30)
    - Weighted average → label

    Returns:
        {
            "compound_score": float,   # weighted blend in [-1, 1]
            "label": str,              # "positive" | "neutral" | "negative"
            "comment_count": int,      # number of non-empty comments analysed
        }
    """
    if not comments:
        return {"compound_score": 0.0, "label": "neutral", "comment_count": 0}

    cleaned = [_clean_text(c) for c in comments if c and c.strip()]
    if not cleaned:
        return {"compound_score": 0.0, "label": "neutral", "comment_count": 0}

    # VADER scores
    vader_scores = [_vader.polarity_scores(c)["compound"] for c in cleaned]
    avg_vader = sum(vader_scores) / len(vader_scores)

    # TextBlob polarity scores
    tb_scores = [TextBlob(c).sentiment.polarity for c in cleaned]
    avg_tb = sum(tb_scores) / len(tb_scores)

    # Weighted blend
    final_score = round(0.70 * avg_vader + 0.30 * avg_tb, 4)

    if final_score >= 0.05:
        label = "positive"
    elif final_score <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return {
        "compound_score": final_score,
        "label": label,
        "comment_count": len(cleaned),
    }
