from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship
from app.database import Base


class CachedUser(Base):
    """Stores fetched Codeforces user profile data."""
    __tablename__ = "cf_users"

    handle = Column(String, primary_key=True, index=True)
    rating = Column(Integer, nullable=True)
    max_rating = Column(Integer, nullable=True)
    rank = Column(String, nullable=True)
    max_rank = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    contribution = Column(Integer, nullable=True)
    registered_at = Column(Integer, nullable=False, default=0)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    submissions = relationship(
        "CachedSubmission",
        foreign_keys="CachedSubmission.handle",
        primaryjoin="CachedUser.handle == CachedSubmission.handle",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    rating_changes = relationship(
        "CachedRatingChange",
        foreign_keys="CachedRatingChange.handle",
        primaryjoin="CachedUser.handle == CachedRatingChange.handle",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class CachedSubmission(Base):
    """Stores fetched Codeforces submission records for a user."""
    __tablename__ = "cf_submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(Integer, nullable=False)
    handle = Column(String, ForeignKey("cf_users.handle", ondelete="CASCADE"), index=True, nullable=False)
    verdict = Column(String, nullable=True)
    problem_name = Column(String, nullable=False)
    problem_rating = Column(Integer, nullable=True)
    tags = Column(String, nullable=True)          # JSON-encoded list of strings
    language = Column(String, nullable=True)
    time_seconds = Column(Integer, nullable=False, default=0)

    user = relationship(
        "CachedUser",
        foreign_keys=[handle],
        back_populates="submissions",
    )

    __table_args__ = (
        Index("ix_cf_submissions_handle_submission", "handle", "submission_id"),
    )


class CachedRatingChange(Base):
    """Stores Codeforces rating history for a user."""
    __tablename__ = "cf_rating_changes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    handle = Column(String, ForeignKey("cf_users.handle", ondelete="CASCADE"), index=True, nullable=False)
    contest_id = Column(Integer, nullable=False)
    contest_name = Column(String, nullable=False)
    rank = Column(Integer, nullable=True)
    old_rating = Column(Integer, nullable=False, default=0)
    new_rating = Column(Integer, nullable=False, default=0)
    time_seconds = Column(Integer, nullable=False, default=0)

    user = relationship(
        "CachedUser",
        foreign_keys=[handle],
        back_populates="rating_changes",
    )
