"""
Database management class for the book library application.
"""

from datetime import date
from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from models import Base, Book, ReadingSession, Note, BookType, ReadingStatus, NoteType
from utils.date_utils import parse_date_input


class DatabaseManager:
    """
    Handles all database operations and provides a clean interface
    for the UI to interact with the data.
    
    This class encapsulates all the SQLAlchemy operations and provides
    high-level methods that the UI can call without needing to know
    about database internals.
    """
    
    def __init__(self, db_path: str = "book_library.db"):
        """Initialize the database connection and create tables if needed."""
        # Create SQLite database engine
        # echo=True would show SQL queries in console (useful for learning)
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        
        # Create all tables if they don't exist
        Base.metadata.create_all(self.engine)
        
        # Create a session factory
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session. Remember to close it when done!"""
        return self.SessionLocal()
    
    # Book operations
    def add_book(self, title: str, author: str, book_type: BookType, 
                 isbn: str = None, publisher: str = None, 
                 publication_year: int = None, pages: int = None) -> Book:
        """Add a new book to the library."""
        with self.get_session() as session:
            book = Book(
                title=title,
                author=author,
                book_type=book_type,
                isbn=isbn,
                publisher=publisher,
                publication_year=publication_year,
                pages=pages
            )
            session.add(book)
            session.commit()
            session.refresh(book)  # Get the assigned ID
            return book
    
    def get_all_books(self) -> List[Book]:
        """Get all books in the library."""
        with self.get_session() as session:
            return session.query(Book).order_by(Book.title).all()
    
    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """Get a specific book by its ID."""
        with self.get_session() as session:
            return session.query(Book).filter(Book.id == book_id).first()
    
    def update_book_status(self, book_id: int, status: ReadingStatus):
        """Update the reading status of a book."""
        with self.get_session() as session:
            book = session.query(Book).filter(Book.id == book_id).first()
            if book:
                book.status = status
                session.commit()
    
    def delete_book(self, book_id: int) -> bool:
        """Delete a book and all its associated data."""
        with self.get_session() as session:
            book = session.query(Book).filter(Book.id == book_id).first()
            if book:
                session.delete(book)
                session.commit()
                return True
            return False
    
    # Author operations for autocomplete
    def get_unique_authors(self) -> List[str]:
        """Get all unique authors from the database."""
        with self.get_session() as session:
            authors = session.query(Book.author).distinct().order_by(Book.author).all()
            return [author[0] for author in authors]
    
    def get_books_by_author(self, author: str) -> List[Book]:
        """Get all books by a specific author."""
        with self.get_session() as session:
            return session.query(Book).filter(Book.author == author).all()
    
    # Reading session operations
    def start_reading_session(self, book_id: int, start_date_str: str = None) -> ReadingSession:
        """
        Start a new reading session for a book.
        
        Args:
            book_id: ID of the book to start reading
            start_date_str: Date string (flexible format) or None for today
        """
        # Parse the date string or use today
        if start_date_str:
            start_date = parse_date_input(start_date_str)
            if not start_date:
                raise ValueError(f"Could not parse date: {start_date_str}")
        else:
            start_date = date.today()
            
        with self.get_session() as session:
            # End any current reading session for this book
            current_session = session.query(ReadingSession).filter(
                ReadingSession.book_id == book_id,
                ReadingSession.end_date.is_(None)
            ).first()
            
            if current_session:
                current_session.end_date = start_date
            
            # Create new session
            new_session = ReadingSession(book_id=book_id, start_date=start_date)
            session.add(new_session)
            
            # Update book status
            book = session.query(Book).filter(Book.id == book_id).first()
            if book:
                book.status = ReadingStatus.READING
            
            session.commit()
            session.refresh(new_session)
            return new_session
    
    def end_reading_session(self, book_id: int, end_date_str: str = None, 
                           session_notes: str = None, completed: bool = False):
        """
        End the current reading session for a book.
        
        Args:
            book_id: ID of the book
            end_date_str: Date string (flexible format) or None for today  
            session_notes: Optional notes about the reading session
            completed: Whether the book was completed in this session
        """
        # Parse the date string or use today
        if end_date_str:
            end_date = parse_date_input(end_date_str)
            if not end_date:
                raise ValueError(f"Could not parse date: {end_date_str}")
        else:
            end_date = date.today()
            
        with self.get_session() as session:
            current_session = session.query(ReadingSession).filter(
                ReadingSession.book_id == book_id,
                ReadingSession.end_date.is_(None)
            ).first()
            
            if current_session:
                current_session.end_date = end_date
                if session_notes:
                    current_session.session_notes = session_notes
                
                # Update book status if completed
                if completed:
                    book = session.query(Book).filter(Book.id == book_id).first()
                    if book:
                        book.status = ReadingStatus.COMPLETED
                
                session.commit()
    
    def get_reading_sessions(self, book_id: int) -> List[ReadingSession]:
        """Get all reading sessions for a book."""
        with self.get_session() as session:
            return session.query(ReadingSession).filter(
                ReadingSession.book_id == book_id
            ).order_by(ReadingSession.start_date.desc()).all()
    
    # Note operations
    def add_note(self, book_id: int, note_type: NoteType, content: str,
                 title: str = None, page_number: int = None) -> Note:
        """Add a note to a book."""
        with self.get_session() as session:
            note = Note(
                book_id=book_id,
                note_type=note_type,
                content=content,
                title=title,
                page_number=page_number
            )
            session.add(note)
            session.commit()
            session.refresh(note)
            return note
    
    def get_notes_for_book(self, book_id: int) -> List[Note]:
        """Get all notes for a specific book."""
        with self.get_session() as session:
            return session.query(Note).filter(
                Note.book_id == book_id
            ).order_by(Note.created_date.desc()).all()
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a specific note."""
        with self.get_session() as session:
            note = session.query(Note).filter(Note.id == note_id).first()
            if note:
                session.delete(note)
                session.commit()
                return True
            return False