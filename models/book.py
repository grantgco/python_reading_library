"""
Book model for the library application.
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base
from .enums import BookType, ReadingStatus


class Book(Base):
    """
    Book model representing a book in the library.
    
    This model stores basic information about each book including:
    - Bibliographic information (title, author, etc.)
    - Book type (physical, ebook, audiobook)
    - Current reading status
    - Timestamps for when added/modified
    """
    __tablename__ = 'books'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic book information
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    isbn = Column(String(20), nullable=True, unique=True)
    publisher = Column(String(255), nullable=True)
    publication_year = Column(Integer, nullable=True)
    pages = Column(Integer, nullable=True)
    
    # Book type and status
    book_type = Column(Enum(BookType), nullable=False, default=BookType.PHYSICAL)
    status = Column(Enum(ReadingStatus), nullable=False, default=ReadingStatus.TO_READ)
    
    # Metadata
    added_date = Column(DateTime, default=func.now())
    last_modified = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships - one book can have many reading sessions and notes
    reading_sessions = relationship("ReadingSession", back_populates="book", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="book", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Book(title='{self.title}', author='{self.author}', status='{self.status.value}')>"