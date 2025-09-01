"""
Reading session model for tracking when books are read.
"""

from datetime import date
from sqlalchemy import Column, Integer, Date, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class ReadingSession(Base):
    """
    Reading session model for tracking when books are read.
    
    As requested, this tracks just the start and end of reading sessions
    rather than daily progress. This makes it easier to manage and less
    overwhelming to track.
    """
    __tablename__ = 'reading_sessions'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to book
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    
    # Session dates - only start and end as requested
    start_date = Column(Date, nullable=False, default=date.today)
    end_date = Column(Date, nullable=True)  # Null if currently reading
    
    # Optional notes about this reading session
    session_notes = Column(Text, nullable=True)
    
    # Metadata
    created_date = Column(DateTime, default=func.now())
    
    # Relationship back to book
    book = relationship("Book", back_populates="reading_sessions")
    
    def __repr__(self):
        end_str = self.end_date.strftime('%Y-%m-%d') if self.end_date else "ongoing"
        return f"<ReadingSession(book='{self.book.title}', start='{self.start_date}', end='{end_str}')>"