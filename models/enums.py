"""
Enumerations used throughout the book library application.
"""

import enum


class BookType(enum.Enum):
    """Enumeration for different types of books"""
    PHYSICAL = "Physical"
    EBOOK = "E-book"
    AUDIOBOOK = "Audiobook"


class ReadingStatus(enum.Enum):
    """Enumeration for reading status"""
    TO_READ = "To Read"
    READING = "Currently Reading"
    COMPLETED = "Completed"
    ABANDONED = "Abandoned"


class NoteType(enum.Enum):
    """Different types of notes that can be attached to books"""
    REVIEW = "Review"
    HIGHLIGHT = "Highlight"
    THOUGHT = "Thought"
    QUOTE = "Quote"