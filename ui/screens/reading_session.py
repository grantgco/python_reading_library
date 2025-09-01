"""
Modal screen for managing reading sessions with flexible date entry.
"""

from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer, Horizontal
from textual.widgets import Button, Input, TextArea, Static, Label, Checkbox
from textual.screen import ModalScreen
from textual import on

from utils.date_utils import parse_date_input, format_date_for_display, validate_date_input


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
    
    @on(Input.Changed, "#date-input")
    def on_input_changed(self, event: Input.Changed) -> None:
        """Update date preview as user types."""
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