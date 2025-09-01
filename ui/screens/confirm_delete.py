"""
Confirmation dialog for dangerous actions.
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Button, Static
from textual.screen import ModalScreen


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