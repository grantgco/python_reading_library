"""
Autocomplete input widget for the book library application.
"""

from typing import List
from textual.app import ComposeResult
from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Container, Vertical
from textual.binding import Binding
from textual.message import Message
from textual import on


class AutocompleteInput(Vertical):
    """
    An input widget with autocomplete suggestions.
    
    This widget shows a dropdown list of suggestions based on the input text.
    Users can navigate suggestions with arrow keys and select with Enter.
    """
    
    DEFAULT_CSS = """
    AutocompleteInput {
        layout: vertical;
        height: auto;
        min-height: 3;
        width: 100%;
    }
    
    AutocompleteInput > Input {
        width: 100%;
        height: 3;
    }
    
    AutocompleteInput > ListView {
        height: 8;
        background: $surface;
        border: solid $primary;
        display: none;
        max-height: 8;
        overflow-y: auto;
    }
    
    AutocompleteInput > ListView.visible {
        display: block;
    }
    
    AutocompleteInput ListView > ListItem {
        height: 1;
        padding: 0 1;
    }
    
    AutocompleteInput ListView > ListItem:focus {
        background: $primary;
        color: $text;
    }
    """
    
    BINDINGS = [
        Binding("down", "select_next", "Next suggestion", show=False),
        Binding("up", "select_previous", "Previous suggestion", show=False),
        Binding("enter", "confirm_selection", "Select", show=False),
        Binding("escape", "hide_suggestions", "Hide", show=False),
    ]
    
    class Submitted(Message):
        """Message sent when the input is submitted."""
        
        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()
    
    def __init__(
        self,
        suggestions: List[str],
        placeholder: str = "",
        value: str = "",
        id: str = None,
        classes: str = None,
    ) -> None:
        """
        Initialize the autocomplete input.
        
        Args:
            suggestions: List of possible suggestions
            placeholder: Placeholder text for the input
            value: Initial value
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(id=id, classes=classes)
        self.all_suggestions = suggestions
        self.filtered_suggestions = []
        self.placeholder = placeholder
        self.initial_value = value
        self.suggestions_visible = False
    
    def compose(self) -> ComposeResult:
        """Compose the autocomplete input widget."""
        yield Input(
            placeholder=self.placeholder,
            value=self.initial_value,
            id="input"
        )
        yield ListView(id="suggestions")
    
    # Widget is focusable as a single unit
    can_focus = True
    
    @on(Input.Changed, "#input")
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input text changes."""
        query = event.value.strip().lower()
        
        if not query:
            self.hide_suggestions()
            return
        
        # Filter suggestions based on input
        self.filtered_suggestions = [
            suggestion for suggestion in self.all_suggestions
            if query in suggestion.lower()
        ]
        
        if self.filtered_suggestions:
            self.show_suggestions()
        else:
            self.hide_suggestions()
    
    @on(Input.Submitted, "#input")
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        self.hide_suggestions()
        self.post_message(self.Submitted(event.value))
    
    def show_suggestions(self) -> None:
        """Show the suggestions list."""
        suggestions_list = self.query_one("#suggestions", ListView)
        suggestions_list.clear()
        
        for suggestion in self.filtered_suggestions[:10]:  # Limit to 10 suggestions
            suggestions_list.append(ListItem(Label(suggestion)))
        
        suggestions_list.add_class("visible")
        self.suggestions_visible = True
    
    def hide_suggestions(self) -> None:
        """Hide the suggestions list."""
        suggestions_list = self.query_one("#suggestions", ListView)
        suggestions_list.remove_class("visible")
        self.suggestions_visible = False
    
    @on(ListView.Selected, "#suggestions")
    def on_suggestion_selected(self, event: ListView.Selected) -> None:
        """Handle suggestion selection."""
        if event.list_view.highlighted_child:
            # Get the selected suggestion text
            label = event.list_view.highlighted_child.query_one(Label)
            selected_text = label.renderable
            
            # Update the input with the selected text
            input_widget = self.query_one("#input", Input)
            input_widget.value = selected_text
            
            # Hide suggestions and focus input
            self.hide_suggestions()
            input_widget.focus()
    
    def action_select_next(self) -> None:
        """Select the next suggestion."""
        if self.suggestions_visible:
            suggestions_list = self.query_one("#suggestions", ListView)
            suggestions_list.action_cursor_down()
    
    def action_select_previous(self) -> None:
        """Select the previous suggestion."""
        if self.suggestions_visible:
            suggestions_list = self.query_one("#suggestions", ListView)
            suggestions_list.action_cursor_up()
    
    def action_confirm_selection(self) -> None:
        """Confirm the current selection."""
        if self.suggestions_visible:
            suggestions_list = self.query_one("#suggestions", ListView)
            if suggestions_list.highlighted_child:
                # Trigger selection
                suggestions_list.action_select_cursor()
                return
        
        # If no suggestion selected, submit the current input
        input_widget = self.query_one("#input", Input)
        self.post_message(self.Submitted(input_widget.value))
    
    def action_hide_suggestions(self) -> None:
        """Hide suggestions and return focus to input."""
        self.hide_suggestions()
        self.query_one("#input").focus()
    
    @property
    def value(self) -> str:
        """Get the current input value."""
        return self.query_one("#input", Input).value
    
    @value.setter
    def value(self, new_value: str) -> None:
        """Set the input value."""
        self.query_one("#input", Input).value = new_value
    
    def focus(self) -> None:
        """Focus the input field."""
        input_widget = self.query_one("#input", Input)
        if input_widget.can_focus:
            input_widget.focus()
            return True
        return False