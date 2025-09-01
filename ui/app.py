"""
Main application class for the book library tracker.
"""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import DataTable, Header, Footer
from textual.binding import Binding

from database import DatabaseManager
from .screens import AddBookScreen, BookDetailScreen
from .styles import APP_CSS


class LibraryApp(App):
    """
    Main application class that manages the book library interface.
    
    This is the entry point for the Textual application. It manages
    screens, handles global actions, and coordinates between the UI
    and database operations.
    """
    
    # CSS styling for the application
    CSS = APP_CSS
    
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
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in the books table."""
        # Get the book ID from the row key and show book details
        book_id = int(event.row_key.value)
        detail_screen = BookDetailScreen(book_id, self.db_manager)
        self.push_screen(detail_screen)
    
    def action_add_book(self) -> None:
        """Show the add book dialog with author autocomplete."""
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
        
        # Get existing authors for autocomplete
        existing_authors = self.db_manager.get_unique_authors()
        
        # Push the modal screen and set up the callback
        add_book_screen = AddBookScreen(existing_authors)
        self.push_screen(add_book_screen, handle_add_book_result)
    
    def action_refresh(self) -> None:
        """Refresh the books table."""
        self.refresh_books_table()
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()