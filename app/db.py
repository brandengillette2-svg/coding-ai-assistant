from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Text, DateTime, Integer, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    description = Column(Text, nullable=False)
    repo_url = Column(String, nullable=False)
    branch = Column(String, default="main")
    status = Column(String, default="pending")  # pending, running, completed, failed
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    steps = relationship("Step", back_populates="task")
    journal_entries = relationship("JournalEntry", back_populates="task")


class Step(Base):
    __tablename__ = "steps"

    id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    name = Column(String, nullable=False)
    kind = Column(String, nullable=False)  # analysis, lookup, edit, execution, verification, review
    description = Column(Text)
    status = Column(String, default="pending")  # pending, running, completed, failed
    output = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    duration_sec = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    task = relationship("Task", back_populates="steps")


class Context(Base):
    __tablename__ = "context"

    id = Column(String, primary_key=True)
    kind = Column(String, nullable=False)  # prior_fix, failed_attempt, symbol_context, repo_summary
    key = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    metadata = Column(JSON, default={})
    embedding = Column(JSON, nullable=True)  # Vector embedding for semantic search
    created_at = Column(DateTime, default=datetime.utcnow)


class JournalEntry(Base):
    __tablename__ = "journal"

    id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    event_type = Column(String, nullable=False)  # task_started, step_completed, verification_passed, etc.
    message = Column(Text)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="journal_entries")


class CodeIndex(Base):
    __tablename__ = "code_index"

    id = Column(String, primary_key=True)
    repo_url = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    symbol_name = Column(String, nullable=False)
    kind = Column(String)  # function, class, method, variable
    signature = Column(Text)
    documentation = Column(Text, nullable=True)
    embedding = Column(JSON, nullable=True)  # Vector embedding
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class VerificationResult(Base):
    __tablename__ = "verification_results"

    id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    passed = Column(Boolean, nullable=False)
    summary = Column(Text)
    details = Column(JSON, default=[])
    output = Column(Text, nullable=True)
    duration_sec = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ReviewResult(Base):
    __tablename__ = "review_results"

    id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    status = Column(String)  # approved, needs_revision, rejected
    summary = Column(Text)
    issues = Column(JSON, default=[])
    recommendations = Column(JSON, default=[])
    reviewer_model = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
