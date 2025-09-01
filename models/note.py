"""
Note model for storing reviews, thoughts, highlights, and quotes.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base
from .enums import NoteType


class Note(Base):
    """
    Note model for storing reviews, thoughts, highlights, and quotes.
    
    This flexible model can store different types of notes related to books:
    - Reviews: Overall thoughts about the book
    - Highlights: Important passages or quotes
    - Thoughts: Random thoughts while reading
    - Quotes: Memorable quotes from the book
    """
    __tablename__ = 'notes'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to book
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    
    # Note information
    note_type = Column(Enum(NoteType), nullable=False)
    title = Column(String(255), nullable=True)  # Optional title for the note
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)  # For highlights/quotes
    
    # Metadata
    created_date = Column(DateTime, default=func.now())
    last_modified = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship back to book
    book = relationship("Book", back_populates="notes")
    
    def __repr__(self):
        return f"<Note(book='{self.book.title}', type='{self.note_type.value}', title='{self.title}')>"