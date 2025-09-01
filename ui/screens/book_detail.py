"""
Screen for viewing and managing details of a specific book.
"""

from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Button, Static, ListView, ListItem, Label, Header, Footer
from textual.screen import Screen
from textual.binding import Binding

from database import DatabaseManager
from models import NoteType
from utils.date_utils import format_date_for_display
from .reading_session import ReadingSessionScreen
from .confirm_delete import ConfirmDeleteScreen


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