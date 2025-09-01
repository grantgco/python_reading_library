"""
CSS styles for the book library application.
"""

APP_CSS = """
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

.error-text {
    color: $error;
    text-style: italic;
    margin: 0 0 1 0;
    text-align: center;
    height: 1;
}
"""