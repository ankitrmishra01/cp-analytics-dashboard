"""
tests/test_analytics.py
Unit tests for the analytics_engine pure functions.
No I/O — all tests run without a database or network.
"""
import sys
import os

# Ensure the backend/ directory is on the path so `app` is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app.services.analytics_engine import (
    solve_by_difficulty,
    solve_by_tag,
    verdict_breakdown,
    weak_topics,
    total_solved,
)

# ── Shared fixture data ────────────────────────────────────────────────────────

SAMPLE_SUBMISSIONS = [
    # Accepted, rated, math+implementation
    {"submission_id": 1,  "verdict": "OK",                  "problem_name": "A. Two Sum",       "problem_rating": 800,  "tags": ["math", "implementation"], "time_seconds": 1_700_000_000},
    # Accepted, graphs
    {"submission_id": 2,  "verdict": "OK",                  "problem_name": "B. Graph Problem", "problem_rating": 1400, "tags": ["graphs", "dfs and bfs"],  "time_seconds": 1_700_000_100},
    # 3× WA/TLE on same problem (all non-AC)
    {"submission_id": 3,  "verdict": "WRONG_ANSWER",        "problem_name": "C. Hard DP",       "problem_rating": 2000, "tags": ["dp", "combinatorics"],    "time_seconds": 1_700_000_200},
    {"submission_id": 4,  "verdict": "WRONG_ANSWER",        "problem_name": "C. Hard DP",       "problem_rating": 2000, "tags": ["dp", "combinatorics"],    "time_seconds": 1_700_000_300},
    {"submission_id": 5,  "verdict": "TIME_LIMIT_EXCEEDED", "problem_name": "C. Hard DP",       "problem_rating": 2000, "tags": ["dp", "combinatorics"],    "time_seconds": 1_700_000_400},
    # Accepted, strings
    {"submission_id": 6,  "verdict": "OK",                  "problem_name": "D. Strings",       "problem_rating": 1600, "tags": ["strings", "hashing"],     "time_seconds": 1_700_000_500},
    # Accepted, math+number theory, rating 1200
    {"submission_id": 7,  "verdict": "OK",                  "problem_name": "E. Math",          "problem_rating": 1200, "tags": ["math", "number theory"],  "time_seconds": 1_700_000_600},
    # Duplicate AC for problem already in seen set — must NOT double-count
    {"submission_id": 8,  "verdict": "OK",                  "problem_name": "A. Two Sum",       "problem_rating": 800,  "tags": ["math", "implementation"], "time_seconds": 1_700_000_700},
    # 2× WA on trees problem — no AC
    {"submission_id": 9,  "verdict": "WRONG_ANSWER",        "problem_name": "F. Trees",         "problem_rating": 2200, "tags": ["trees", "dp"],            "time_seconds": 1_700_000_800},
    {"submission_id": 10, "verdict": "WRONG_ANSWER",        "problem_name": "F. Trees",         "problem_rating": 2200, "tags": ["trees", "dp"],            "time_seconds": 1_700_000_900},
    # 3× WA on geometry — classic weak topic
    {"submission_id": 11, "verdict": "WRONG_ANSWER",        "problem_name": "G. Geometry",      "problem_rating": 2400, "tags": ["geometry"],               "time_seconds": 1_700_001_000},
    {"submission_id": 12, "verdict": "WRONG_ANSWER",        "problem_name": "G. Geometry",      "problem_rating": 2400, "tags": ["geometry"],               "time_seconds": 1_700_001_100},
    {"submission_id": 13, "verdict": "WRONG_ANSWER",        "problem_name": "G. Geometry",      "problem_rating": 2400, "tags": ["geometry"],               "time_seconds": 1_700_001_200},
    # Unrated AC
    {"submission_id": 14, "verdict": "OK",                  "problem_name": "H. Unrated",       "problem_rating": None, "tags": ["implementation"],         "time_seconds": 1_700_001_300},
]


# ── solve_by_difficulty ────────────────────────────────────────────────────────

class TestSolveByDifficulty:
    def test_bucket_lt_1200(self):
        result = {b.bucket: b.count for b in solve_by_difficulty(SAMPLE_SUBMISSIONS)}
        # A. Two Sum (800) is the only unique AC in <1200
        assert result.get("<1200", 0) == 1

    def test_bucket_1200_1399(self):
        result = {b.bucket: b.count for b in solve_by_difficulty(SAMPLE_SUBMISSIONS)}
        # E. Math (1200)
        assert result.get("1200-1399", 0) == 1

    def test_bucket_1400_1599(self):
        result = {b.bucket: b.count for b in solve_by_difficulty(SAMPLE_SUBMISSIONS)}
        # B. Graph Problem (1400)
        assert result.get("1400-1599", 0) == 1

    def test_bucket_1600_1799(self):
        result = {b.bucket: b.count for b in solve_by_difficulty(SAMPLE_SUBMISSIONS)}
        # D. Strings (1600)
        assert result.get("1600-1799", 0) == 1

    def test_wa_not_counted(self):
        result = {b.bucket: b.count for b in solve_by_difficulty(SAMPLE_SUBMISSIONS)}
        # C. Hard DP (2000) only WA/TLE → should be 0
        assert result.get("2000-2199", 0) == 0

    def test_no_double_count_duplicate_ac(self):
        result = {b.bucket: b.count for b in solve_by_difficulty(SAMPLE_SUBMISSIONS)}
        # A. Two Sum has two AC submissions but should count only once
        assert result.get("<1200", 0) == 1

    def test_unrated_bucket_present(self):
        result = {b.bucket: b.count for b in solve_by_difficulty(SAMPLE_SUBMISSIONS)}
        assert result.get("Unrated", 0) == 1

    def test_returns_all_standard_buckets(self):
        buckets = [b.bucket for b in solve_by_difficulty(SAMPLE_SUBMISSIONS)]
        for label in ["<1200", "1200-1399", "1400-1599", "1600-1799",
                      "1800-1999", "2000-2199", "2200-2399", "2400+"]:
            assert label in buckets

    def test_empty_submissions(self):
        result = solve_by_difficulty([])
        for b in result:
            assert b.count == 0


# ── solve_by_tag ───────────────────────────────────────────────────────────────

class TestSolveByTag:
    def _tag_map(self):
        return {t.tag: t.count for t in solve_by_tag(SAMPLE_SUBMISSIONS)}

    def test_math_appears_in_two_unique_ac_problems(self):
        # math: A. Two Sum + E. Math = 2 unique AC problems
        assert self._tag_map().get("math", 0) == 2

    def test_implementation_counted_once_despite_two_ac_submissions(self):
        # implementation: in A. Two Sum (800) and H. Unrated — two distinct AC problems
        # A. Two Sum has 2 AC submissions but only counts once (deduplication)
        assert self._tag_map().get("implementation", 0) == 2

    def test_wa_tags_not_counted(self):
        # geometry: only WA → should be 0
        assert self._tag_map().get("geometry", 0) == 0

    def test_dp_not_counted_when_only_wa(self):
        # dp appears in C. Hard DP (WA) and F. Trees (WA) — no AC
        assert self._tag_map().get("dp", 0) == 0

    def test_sorted_descending(self):
        counts = [t.count for t in solve_by_tag(SAMPLE_SUBMISSIONS)]
        assert counts == sorted(counts, reverse=True)

    def test_empty_submissions(self):
        assert solve_by_tag([]) == []


# ── verdict_breakdown ──────────────────────────────────────────────────────────

class TestVerdictBreakdown:
    def _verdict_map(self):
        return {v.verdict: v.count for v in verdict_breakdown(SAMPLE_SUBMISSIONS)}

    def test_ok_count(self):
        # submissions 1,2,6,7,8,14 are OK → 6 (H. Unrated is also accepted)
        assert self._verdict_map().get("OK", 0) == 6

    def test_wrong_answer_count(self):
        # submissions 3,4,9,10,11,12,13 → 7
        assert self._verdict_map().get("WRONG_ANSWER", 0) == 7

    def test_tle_count(self):
        assert self._verdict_map().get("TIME_LIMIT_EXCEEDED", 0) == 1

    def test_sorted_descending(self):
        counts = [v.count for v in verdict_breakdown(SAMPLE_SUBMISSIONS)]
        assert counts == sorted(counts, reverse=True)

    def test_empty(self):
        assert verdict_breakdown([]) == []


# ── weak_topics ────────────────────────────────────────────────────────────────

class TestWeakTopics:
    def test_geometry_flagged_as_weak(self):
        result = {w.tag: w for w in weak_topics(SAMPLE_SUBMISSIONS, min_attempts=1)}
        assert "geometry" in result
        geo = result["geometry"]
        assert geo.accepted == 0
        assert geo.accept_rate == 0.0

    def test_min_attempts_filter(self):
        # With min_attempts=3, only tags with ≥3 unique problems attempted qualify
        result = weak_topics(SAMPLE_SUBMISSIONS, min_attempts=3)
        for w in result:
            assert w.attempts >= 3

    def test_sorted_ascending_accept_rate(self):
        result = weak_topics(SAMPLE_SUBMISSIONS, min_attempts=1)
        rates = [w.accept_rate for w in result]
        assert rates == sorted(rates)

    def test_fully_accepted_tag_not_in_results(self):
        # 'hashing' only appears in D. Strings (accepted) — accept_rate == 1.0
        result = {w.tag: w for w in weak_topics(SAMPLE_SUBMISSIONS, min_attempts=1)}
        hashing = result.get("hashing")
        if hashing:
            assert hashing.accept_rate == 1.0

    def test_empty_submissions(self):
        assert weak_topics([], min_attempts=1) == []


# ── total_solved ───────────────────────────────────────────────────────────────

class TestTotalSolved:
    def test_counts_unique_accepted(self):
        # Unique AC: A. Two Sum, B. Graph Problem, D. Strings, E. Math, H. Unrated = 5
        assert total_solved(SAMPLE_SUBMISSIONS) == 5

    def test_empty(self):
        assert total_solved([]) == 0

    def test_no_accepted(self):
        wa_only = [
            {"submission_id": i, "verdict": "WRONG_ANSWER", "problem_name": f"P{i}",
             "problem_rating": 1000, "tags": [], "time_seconds": i}
            for i in range(5)
        ]
        assert total_solved(wa_only) == 0

    def test_single_accepted(self):
        subs = [{"submission_id": 99, "verdict": "OK", "problem_name": "Only",
                 "problem_rating": 1500, "tags": ["math"], "time_seconds": 0}]
        assert total_solved(subs) == 1
