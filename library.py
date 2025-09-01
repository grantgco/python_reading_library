#!/usr/bin/env python3
"""
Personal Book Library Tracker
A SQLite-based textual UI application for tracking books, reading sessions, and notes.

This script demonstrates:
- SQLAlchemy ORM for database management
- Textual TUI framework for creating terminal interfaces
- Database design with relationships
- CRUD operations in a user-friendly interface

Author: Learning Python & Textual
"""

import asyncio
from datetime import datetime, date
from typing import Optional, List
from pathlib import Path

# Date parsing library - install with: pip install python-dateutil
from dateutil.parser import parse as parse_date
from dateutil.parser import ParserError

# Database imports
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Date, Boolean, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session  # Updated import for SQLAlchemy 2.0+
from sqlalchemy.sql import func
import enum

# Textual UI imports
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Button, Input, TextArea, Static, DataTable, Select, Header, Footer,
    ListView, ListItem, Label, Checkbox
)
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from textual import on
from textual.validation import Function, ValidationResult, Validator

# Database Models
# ===============

# Create the base class for our database models
Base = declarative_base()

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

class NoteType(enum.Enum):
    """Different types of notes that can be attached to books"""
    REVIEW = "Review"
    HIGHLIGHT = "Highlight"
    THOUGHT = "Thought"
    QUOTE = "Quote"

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

# Utility Functions
# =================

def parse_date_input(date_string: str) -> Optional[date]:
    """
    Parse a date string into a date object using dateutil.
    
    This function is very forgiving and can handle many date formats:
    - "2023-12-25" (ISO format)
    - "12/25/2023" (US format)
    - "25/12/2023" (European format) 
    - "Dec 25, 2023" (text format)
    - "yesterday", "today", "tomorrow" (relative)
    - "last monday", "next friday" (relative days)
    - And many more!
    
    Args:
        date_string: The date string to parse
        
    Returns:
        date object if parsing succeeds, None if it fails
        
    Examples:
        >>> parse_date_input("2023-12-25")
        datetime.date(2023, 12, 25)
        >>> parse_date_input("Dec 25, 2023")  
        datetime.date(2023, 12, 25)
        >>> parse_date_input("yesterday")
        datetime.date(2023, 12, 24)  # Assuming today is 2023-12-25
    """
    if not date_string or not date_string.strip():
        return None
    
    try:
        # dateutil.parser.parse is very flexible
        parsed_datetime = parse_date(date_string.strip())
        # Convert datetime to date (we only need the date part)
        return parsed_datetime.date()
    except (ParserError, ValueError, TypeError):
        return None

def format_date_for_display(date_obj: date) -> str:
    """
    Format a date object for display in the UI.
    
    Args:
        date_obj: The date to format
        
    Returns:
        Formatted date string
    """
    if not date_obj:
        return ""
    return date_obj.strftime("%Y-%m-%d (%a)")  # e.g., "2023-12-25 (Mon)"

def validate_date_input(date_string: str) -> bool:
    """
    Validate if a date string can be parsed.
    
    Args:
        date_string: The date string to validate
        
    Returns:
        True if the date can be parsed, False otherwise
    """
    return parse_date_input(date_string) is not None

# Database Management Class
# =========================

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

# Textual UI Components
# =====================

class AddBookScreen(ModalScreen):
    """
    Modal screen for adding a new book to the library.
    
    This demonstrates how to create modal dialogs in Textual.
    Modal screens appear on top of the main screen and can
    return data to the parent screen when closed.
    
    Sizing approaches demonstrated:
    1. Fixed size (current): Set specific width/height in CSS
    2. Responsive: Use percentages with max/min constraints
    3. Auto-sizing: Let content determine size with constraints
    4. Scrollable: Wrap content in ScrollableContainer for overflow
    """
    
    def compose(self) -> ComposeResult:
        """Compose the UI elements for the add book form."""
        with Container(id="add-book-dialog"):
            yield Static("Add New Book", classes="dialog-title")
            
            # Option 4: Scrollable content (uncomment the ScrollableContainer lines to enable)
            # with ScrollableContainer(classes="dialog-content"):
            with Vertical(classes="dialog-content"):
                yield Label("Title:")
                yield Input(placeholder="Enter book title", id="title-input")
                
                yield Label("Author:")
                yield Input(placeholder="Enter author name", id="author-input")
                
                yield Label("Book Type:")
                yield Select(
                    options=[(book_type.value, book_type) for book_type in BookType],
                    value=BookType.PHYSICAL,
                    id="type-select"
                )
                
                yield Label("ISBN (optional):")
                yield Input(placeholder="Enter ISBN", id="isbn-input")
                
                yield Label("Publisher (optional):")
                yield Input(placeholder="Enter publisher", id="publisher-input")
                
                yield Label("Publication Year (optional):")
                yield Input(placeholder="Enter year", id="year-input")
                
                yield Label("Pages (optional):")
                yield Input(placeholder="Enter page count", id="pages-input")
                
                # Additional fields that might require scrolling
                yield Label("Genre (optional):")
                yield Input(placeholder="Enter genre", id="genre-input")
                
                yield Label("Description (optional):")
                yield TextArea(placeholder="Enter book description", id="description-input")
                
                with Horizontal(classes="dialog-buttons"):
                    yield Button("Cancel", variant="default", id="cancel-btn")
                    yield Button("Add Book", variant="primary", id="add-btn")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses in the dialog."""
        if event.button.id == "cancel-btn":
            self.dismiss(None)  # Return None to indicate cancellation
        elif event.button.id == "add-btn":
            # Collect form data
            title = self.query_one("#title-input").value.strip()
            author = self.query_one("#author-input").value.strip()
            
            # Basic validation
            if not title or not author:
                # In a real app, you'd show an error message
                return
            
            # Collect optional fields
            book_type = self.query_one("#type-select").value
            isbn = self.query_one("#isbn-input").value.strip() or None
            publisher = self.query_one("#publisher-input").value.strip() or None
            
            # Handle numeric fields with error checking
            year_str = self.query_one("#year-input").value.strip()
            year = int(year_str) if year_str.isdigit() else None
            
            pages_str = self.query_one("#pages-input").value.strip()
            pages = int(pages_str) if pages_str.isdigit() else None
            
            # Additional optional fields (for scrolling demo)
            genre = self.query_one("#genre-input").value.strip() or None
            description = self.query_one("#description-input").text.strip() or None
            
            # Return the book data
            book_data = {
                'title': title,
                'author': author,
                'book_type': book_type,
                'isbn': isbn,
                'publisher': publisher,
                'publication_year': year,
                'pages': pages,
                # Note: genre and description aren't in the DB model,
                # but this shows how you'd handle additional fields
                'genre': genre,
                'description': description
            }
            self.dismiss(book_data)

class ConfirmDeleteScreen(ModalScreen):
    """Simple confirmation dialog for dangerous actions."""
    
    def __init__(self, message: str, book_title: str):
        super().__init__()
        self.message = message
        self.book_title = book_title
    
    def compose(self) -> ComposeResult:
        with Container(id="confirm-dialog"):
            yield Static("Confirm Delete", classes="dialog-title")
            with Vertical(classes="dialog-content"):
                yield Static(self.message, classes="confirm-message")
                yield Static(f'Book: "{self.book_title}"', classes="book-title-confirm")
                yield Static("This action cannot be undone!", classes="warning-text")
                
                with Horizontal(classes="dialog-buttons"):
                    yield Button("Cancel", variant="default", id="cancel-btn")
                    yield Button("Delete", variant="error", id="delete-btn")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self.dismiss(False)  # User cancelled
        elif event.button.id == "delete-btn":
            self.dismiss(True)   # User confirmed deletion

class ReadingSessionScreen(ModalScreen):
    """
    Modal screen for managing reading sessions with flexible date entry.
    
    This demonstrates how to use dateutil for parsing user-entered dates.
    Users can enter dates in many formats:
    - "2023-12-25", "12/25/2023", "Dec 25, 2023" 
    - "today", "yesterday", "tomorrow"
    - "last monday", "next friday"
    - And many more natural language formats!
    """
    
    def __init__(self, book_id: int, book_title: str, action: str = "start"):
        """
        Initialize the reading session screen.
        
        Args:
            book_id: ID of the book
            book_title: Title of the book (for display)
            action: Either "start" or "end"
        """
        super().__init__()
        self.book_id = book_id
        self.book_title = book_title
        self.action = action
    
    def compose(self) -> ComposeResult:
        """Compose the reading session form."""
        title = f"{'Start' if self.action == 'start' else 'End'} Reading Session"
        
        with Container(id="session-dialog"):
            yield Static(title, classes="dialog-title")
            with ScrollableContainer(classes="dialog-content"):
                yield Static(f"Book: {self.book_title}", classes="book-info")
                
                yield Label(f"{'Start' if self.action == 'start' else 'End'} Date:")
                yield Input(
                    placeholder="Enter date (e.g., 'today', '2023-12-25', 'Dec 25', 'yesterday')",
                    id="date-input",
                    value="today"  # Default to today
                )
                yield Static("", id="date-preview", classes="date-preview")
                
                if self.action == "end":
                    yield Label("Mark as completed?")
                    yield Checkbox("Book completed", id="completed-checkbox")
                
                yield Label("Session Notes (optional):")
                yield TextArea(
                    placeholder="Enter notes about this reading session...",
                    id="notes-input"
                )
                
                with Horizontal(classes="dialog-buttons"):
                    yield Button("Cancel", variant="default", id="cancel-btn")
                    yield Button(
                        f"{'Start' if self.action == 'start' else 'End'} Session", 
                        variant="primary", 
                        id="action-btn"
                    )
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Update date preview as user types."""
        if event.input.id == "date-input":
            date_str = event.value.strip()
            preview = self.query_one("#date-preview")
            
            if not date_str:
                preview.update("")
                return
                
            parsed_date = parse_date_input(date_str)
            if parsed_date:
                formatted = format_date_for_display(parsed_date)
                preview.update(f"✓ Parsed as: {formatted}")
                preview.set_class(True, "valid-date")
                preview.set_class(False, "invalid-date")
            else:
                preview.update(f"✗ Could not parse: {date_str}")
                preview.set_class(False, "valid-date")
                preview.set_class(True, "invalid-date")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-btn":
            self.dismiss(None)
        elif event.button.id == "action-btn":
            # Validate and collect form data
            date_str = self.query_one("#date-input").value.strip()
            notes = self.query_one("#notes-input").text.strip() or None
            
            if not date_str:
                # Show error - in a real app, you'd have proper error handling
                return
            
            # Validate date can be parsed
            if not validate_date_input(date_str):
                # Show error - date couldn't be parsed
                return
            
            session_data = {
                'date_str': date_str,
                'notes': notes,
                'action': self.action
            }
            
            if self.action == "end":
                completed = self.query_one("#completed-checkbox").value
                session_data['completed'] = completed
            
            self.dismiss(session_data)

class BookDetailScreen(Screen):
    """
    Screen for viewing and managing details of a specific book.
    
    This screen shows:
    - Book information
    - Reading sessions
    - Notes/highlights/reviews
    - Actions (start/end reading, add notes, etc.)
    """
    
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("n", "add_note", "Add Note"),
        Binding("s", "start_reading", "Start Reading"),
        Binding("e", "end_reading", "End Reading"),
        Binding("d", "delete_book", "Delete Book"),
        ]
    
    def __init__(self, book_id: int, db_manager: DatabaseManager):
        super().__init__()
        self.book_id = book_id
        self.db_manager = db_manager
        self.book = None
    
    def compose(self) -> ComposeResult:
        """Compose the book detail view."""
        yield Header()
        
        with ScrollableContainer():
            yield Static("", id="book-info")
            yield Static("Reading Sessions", classes="section-title")
            yield Static("", id="sessions-info")
            yield Static("Notes & Highlights", classes="section-title")
            yield ListView(id="notes-list")
            
        with Container(classes="action-bar"):
            yield Button("Start Reading", id="start-reading-btn")
            yield Button("End Reading", id="end-reading-btn")
            yield Button("Add Note", id="add-note-btn")
            yield Button("Back", id="back-btn")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Load book data when screen is mounted."""
        self.load_book_data()
    
    def load_book_data(self) -> None:
        """Load and display book information."""
        self.book = self.db_manager.get_book_by_id(self.book_id)
        if not self.book:
            return
        
        # Update book info display
        info_text = f"""Title: {self.book.title}
Author: {self.book.author}
Type: {self.book.book_type.value}
Status: {self.book.status.value}
Added: {self.book.added_date.strftime('%Y-%m-%d')}"""
        
        if self.book.isbn:
            info_text += f"\nISBN: {self.book.isbn}"
        if self.book.publisher:
            info_text += f"\nPublisher: {self.book.publisher}"
        if self.book.publication_year:
            info_text += f"\nYear: {self.book.publication_year}"
        if self.book.pages:
            info_text += f"\nPages: {self.book.pages}"
        
        self.query_one("#book-info").update(info_text)
        
        # Load reading sessions
        sessions = self.db_manager.get_reading_sessions(self.book_id)
        if sessions:
            sessions_text = "\n".join([
                f"• {format_date_for_display(session.start_date)} - "
                f"{format_date_for_display(session.end_date) if session.end_date else 'ongoing'}"
                + (f": {session.session_notes}" if session.session_notes else "")
                for session in sessions
            ])
        else:
            sessions_text = "No reading sessions yet."
        self.query_one("#sessions-info").update(sessions_text)
        
        # Load notes
        notes = self.db_manager.get_notes_for_book(self.book_id)
        notes_list = self.query_one("#notes-list")
        notes_list.clear()
        
        for note in notes:
            note_text = f"[{note.note_type.value}] "
            if note.title:
                note_text += f"{note.title}: "
            note_text += note.content[:100] + ("..." if len(note.content) > 100 else "")
            if note.page_number:
                note_text += f" (p. {note.page_number})"
            
            notes_list.append(ListItem(Label(note_text)))
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back-btn":
            self.action_back()
        elif event.button.id == "start-reading-btn":
            self.action_start_reading()
        elif event.button.id == "end-reading-btn":
            self.action_end_reading()
        elif event.button.id == "add-note-btn":
            self.action_add_note()
    
    def action_back(self) -> None:
        """Go back to the main screen."""
        self.app.pop_screen()
    
    def action_start_reading(self) -> None:
        """Start a reading session for this book."""
        def handle_session_result(session_data):
            """Handle the result from the reading session dialog."""
            if session_data:  # User didn't cancel
                try:
                    self.db_manager.start_reading_session(
                        self.book_id, 
                        session_data['date_str']
                    )
                    self.load_book_data()  # Refresh the display
                except ValueError as e:
                    # Date parsing error
                    self.bell()
                except Exception as e:
                    # Other error
                    self.bell()
        
        # Show the reading session dialog
        session_screen = ReadingSessionScreen(
            self.book_id, 
            self.book.title, 
            action="start"
        )
        self.app.push_screen(session_screen, handle_session_result)
    
    def action_end_reading(self) -> None:
        """End the current reading session."""
        def handle_session_result(session_data):
            """Handle the result from the reading session dialog."""
            if session_data:  # User didn't cancel
                try:
                    self.db_manager.end_reading_session(
                        self.book_id,
                        session_data['date_str'],
                        session_data.get('notes'),
                        session_data.get('completed', False)
                    )
                    self.load_book_data()  # Refresh the display
                except ValueError as e:
                    # Date parsing error
                    self.bell()
                except Exception as e:
                    # Other error
                    self.bell()
        
        # Show the reading session dialog
        session_screen = ReadingSessionScreen(
            self.book_id, 
            self.book.title, 
            action="end"
        )
        self.app.push_screen(session_screen, handle_session_result)
    
    def action_add_note(self) -> None:
        """Add a note to this book."""
        # In a real implementation, you'd show a modal dialog for adding notes
        # For now, just add a sample note
        self.db_manager.add_note(
            self.book_id, 
            NoteType.THOUGHT, 
            "Sample thought added from UI",
            title="UI Test Note"
        )
        self.load_book_data()  # Refresh the display

    def action_delete_book(self) -> None:
        """Delete the current book with confirmation."""
        def handle_confirmation(confirmed: bool):
            """Handle the result from the confirmation dialog."""
            if confirmed:  # User confirmed deletion
                try:
                    success = self.db_manager.delete_book(self.book_id)
                    if success:
                        # Go back to main screen after successful deletion
                        self.app.pop_screen()
                    else:
                        # In a real app, show error message
                        self.bell()  # Make error sound
                except Exception as e:
                    # Handle any database errors
                    self.bell()
    
        # Show confirmation dialog
        confirm_screen = ConfirmDeleteScreen(
            "Are you sure you want to delete this book?",
            self.book.title if self.book else "Unknown"
        )
        self.app.push_screen(confirm_screen, handle_confirmation)


class LibraryApp(App):
    """
    Main application class that manages the book library interface.
    
    This is the entry point for the Textual application. It manages
    screens, handles global actions, and coordinates between the UI
    and database operations.
    """
    
    # CSS styling for the application
    CSS = """
    /* Main modal dialog styling */
    #add-book-dialog, #session-dialog {
        width: 80;
        height: 35;
        border: thick $background;
        background: $surface;
        margin: 1 2;
    }
    
    .dialog-title {
        dock: top;
        text-align: center;
        background: $primary;
        color: $text;
        height: 1;
        content-align: center middle;
    }
    
    .dialog-content {
        padding: 1 2;
        height: 1fr;
        overflow-y: auto;
    }
    
    .dialog-buttons {
        dock: bottom;
        height: 3;
        align: right middle;
        margin: 1;
        background: $surface;
    }
    
    /* Date parsing preview styles */
    .date-preview {
        height: 1;
        margin: 0 0 1 0;
        text-style: italic;
    }
    
    .valid-date {
        color: $success;
    }
    
    .invalid-date {
        color: $error;
    }
    
    .book-info {
        background: $primary-background;
        padding: 0 1;
        margin: 0 0 1 0;
        text-style: bold;
    }
    
    .section-title {
        background: $primary;
        color: $text;
        padding: 0 1;
        margin: 1 0;
    }
    
    .action-bar {
        dock: bottom;
        height: 3;
        background: $surface;
        padding: 1;
    }
    
    DataTable {
        height: 1fr;
    }

    #confirm-dialog {
    width: 60;
    height: 15;
    border: thick $error;
    background: $surface;
    margin: 1 2;
    }

    .confirm-message {
        text-align: center;
        margin: 1 0;
    }

    .book-title-confirm {
        text-align: center;
        text-style: bold;
        margin: 0 0 1 0;
    }

    .warning-text {
        text-align: center;
        color: $error;
        text-style: italic;
        margin: 0 0 1 0;
    }
    """
    
    # Key bindings for the main screen
    BINDINGS = [
        Binding("a", "add_book", "Add Book"),
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
    
    def compose(self) -> ComposeResult:
        """Compose the main application layout."""
        yield Header()
        
        with Container():
            # Create a data table to display books
            table = DataTable(id="books-table", cursor_type="row")
            table.add_columns("Title", "Author", "Type", "Status", "Added")
            yield table
        
        # with Container(classes="action-bar"):
        #     yield Button("Add Book", id="add-book-btn", variant="primary")
        #     yield Button("Refresh", id="refresh-btn")
        #     yield Button("Quit", id="quit-btn")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the application when it starts."""
        self.title = "Personal Book Library Tracker"
        self.sub_title = "Track your reading journey with Python & Textual"
        self.refresh_books_table()
        # Auto-focus the table for keyboard navigation
        self.query_one("#books-table").focus()
    
    def refresh_books_table(self) -> None:
        """Refresh the books table with current data."""
        table = self.query_one("#books-table")
        table.clear()
        
        books = self.db_manager.get_all_books()
        for book in books:
            table.add_row(
                book.title,
                book.author,
                book.book_type.value,
                book.status.value,
                book.added_date.strftime('%Y-%m-%d'),
                key=str(book.id)  # Store book ID as row key for later reference
            )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "add-book-btn":
            self.action_add_book()
        elif event.button.id == "refresh-btn":
            self.action_refresh()
        elif event.button.id == "quit-btn":
            self.action_quit()
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in the books table."""
        # Get the book ID from the row key and show book details
        book_id = int(event.row_key.value)
        detail_screen = BookDetailScreen(book_id, self.db_manager)
        self.push_screen(detail_screen)
    
    def action_add_book(self) -> None:
        """Show the add book dialog."""
        def handle_add_book_result(book_data):
            """Callback function to handle the result from add book dialog."""
            if book_data:  # User didn't cancel
                try:
                    # Remove any extra fields that aren't in the database model
                    # (like genre and description which were added for the scrolling demo)
                    db_fields = {
                        'title', 'author', 'book_type', 'isbn', 
                        'publisher', 'publication_year', 'pages'
                    }
                    filtered_data = {k: v for k, v in book_data.items() if k in db_fields}
                    
                    self.db_manager.add_book(**filtered_data)
                    self.refresh_books_table()
                except Exception as e:
                    # In a real app, you'd show a proper error dialog
                    self.bell()  # Make a sound to indicate error
        
        # Push the modal screen and set up the callback
        add_book_screen = AddBookScreen()
        self.push_screen(add_book_screen, handle_add_book_result)
    
    def action_refresh(self) -> None:
        """Refresh the books table."""
        self.refresh_books_table()
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

# Main entry point
# ================

def main():
    """
    Main function to run the application.
    
    This function creates and runs the Textual application.
    It's the entry point when the script is run directly.
    """
    # Create and run the application
    app = LibraryApp()
    app.run()

if __name__ == "__main__":
    # Only run the app if this script is executed directly
    # (not imported as a module)
    main()