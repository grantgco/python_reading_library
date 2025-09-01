"""
Modal screen for adding a new book with author autocomplete.
"""

from typing import List
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Button, Input, TextArea, Static, Select, Label
from textual.screen import ModalScreen
from textual.binding import Binding

from models import BookType
from ui.widgets import AutocompleteInput


class AddBookScreen(ModalScreen):
    """
    Modal screen for adding a new book to the library.
    
    This screen includes author autocomplete functionality to help users
    quickly enter authors that already exist in the database.
    """
    
    BINDINGS = [
        Binding("ctrl+enter", "submit", "Submit", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]
    
    def __init__(self, existing_authors: List[str] = None):
        """
        Initialize the add book screen.
        
        Args:
            existing_authors: List of authors already in the database for autocomplete
        """
        super().__init__()
        self.existing_authors = existing_authors or []
    
    def compose(self) -> ComposeResult:
        """Compose the UI elements for the add book form."""
        with Container(id="add-book-dialog"):
            yield Static("Add New Book", classes="dialog-title")
            
            with Vertical(classes="dialog-content"):
                yield Static("", id="error-message", classes="error-text")
                
                yield Label("Title:")
                yield Input(placeholder="Enter book title", id="title-input")
                
                yield Label("Author:")
                yield AutocompleteInput(
                    suggestions=self.existing_authors,
                    placeholder="Enter author name",
                    id="author-input"
                )
                
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
    
    def on_mount(self) -> None:
        """Set up initial focus when modal opens."""
        self.query_one("#title-input").focus()
    
    def action_submit(self) -> None:
        """Submit the form via keyboard shortcut."""
        self._submit_form()
    
    def action_cancel(self) -> None:
        """Cancel the form via keyboard shortcut."""
        self.dismiss(None)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses in the dialog."""
        if event.button.id == "cancel-btn":
            self.dismiss(None)  # Return None to indicate cancellation
        elif event.button.id == "add-btn":
            self._submit_form()
    
    def _submit_form(self) -> None:
        """Submit the form with validation."""
        # Clear previous error message
        self.query_one("#error-message").update("")
        
        # Collect form data
        title = self.query_one("#title-input").value.strip()
        author = self.query_one("#author-input").value.strip()
        
        # Validate required fields
        if not title:
            self.query_one("#error-message").update("Title is required")
            self.query_one("#title-input").focus()
            return
            
        if not author:
            self.query_one("#error-message").update("Author is required")
            self.query_one("#author-input").focus()
            return
        
        # Collect optional fields
        book_type = self.query_one("#type-select").value
        isbn = self.query_one("#isbn-input").value.strip() or None
        publisher = self.query_one("#publisher-input").value.strip() or None
        
        # Handle numeric fields with error checking
        year_str = self.query_one("#year-input").value.strip()
        year = None
        if year_str:
            try:
                year = int(year_str)
            except ValueError:
                self.query_one("#error-message").update("Publication year must be a number")
                self.query_one("#year-input").focus()
                return
        
        pages_str = self.query_one("#pages-input").value.strip()
        pages = None
        if pages_str:
            try:
                pages = int(pages_str)
            except ValueError:
                self.query_one("#error-message").update("Pages must be a number")
                self.query_one("#pages-input").focus()
                return
        
        # Additional optional fields
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
            'genre': genre,
            'description': description
        }
        self.dismiss(book_data)