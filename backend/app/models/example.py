"""
Example database model.
This file demonstrates how to create models using SQLAlchemy.
"""
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ExampleModel(Base):
    """
    Example model demonstrating SQLAlchemy ORM usage.
    
    This is a template - replace with your actual models.
    """
    __tablename__ = "examples"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    
    def __repr__(self) -> str:
        return f"<ExampleModel(id={self.id}, name='{self.name}')>"

