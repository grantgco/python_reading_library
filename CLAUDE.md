# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a Personal Book Library Tracker - a SQLite-based terminal user interface (TUI) application built with Python. The application allows users to track books, reading sessions, and notes through a modern terminal interface. **Version 2.0** features a modular architecture with author autocomplete functionality.

## Architecture

### Modular Structure
```
library/
├── models/          # Database models and enums
├── database/        # Database management layer  
├── ui/              # User interface components
│   ├── screens/     # Individual screen classes
│   ├── widgets/     # Custom widgets (autocomplete)
│   └── styles/      # CSS styling
├── utils/           # Utility functions
├── main.py          # Application entry point
└── requirements.txt # Dependencies
```

### Core Components
- **Database Layer**: SQLAlchemy ORM with SQLite backend (`book_library.db`)
- **UI Framework**: Textual TUI framework for terminal-based interface  
- **Models**: Modular entities - Book, ReadingSession, Note with relationships
- **Custom Widgets**: AutocompleteInput for enhanced user experience
- **Application Structure**: Clean separation of concerns across modules

### Database Schema
- **Book**: Core book information (title, author, ISBN, type, status, metadata)
- **ReadingSession**: Start/end dates for reading periods (simplified tracking)
- **Note**: Flexible notes system (reviews, highlights, thoughts, quotes)

### UI Architecture
- **LibraryApp**: Main application with DataTable for book listing (`ui/app.py`)
- **BookDetailScreen**: Screen for viewing/managing individual books (`ui/screens/book_detail.py`)
- **Modal Screens**: AddBookScreen (with autocomplete), ReadingSessionScreen, ConfirmDeleteScreen
- **DatabaseManager**: Centralized database operations with session management (`database/manager.py`)

## Key Features
- **Author Autocomplete**: Smart suggestions based on existing authors in database
- **Flexible Date Parsing**: Natural language date input using `python-dateutil` 
- **Modal Dialog System**: User-friendly interaction patterns
- **Modular Architecture**: Clean code organization for maintainability
- **Relationship-based Data Model**: Cascading deletes and proper foreign keys
- **Reading Session Tracking**: Simple start/end tracking with completion marking
- **Multi-type Note System**: Support for reviews, highlights, thoughts, quotes

## Running the Application

### Prerequisites
```bash
pip install -r requirements.txt
# Or manually:
# pip install sqlalchemy textual python-dateutil
```

### Start Application
```bash
cd library
python3 main.py
```

The application will create `book_library.db` automatically on first run.

### Key Bindings (Main Screen)
- `a`: Add new book (with author autocomplete)
- `r`: Refresh book list  
- `q`: Quit application
- `Enter`: View book details

### Key Bindings (Book Detail Screen)
- `n`: Add note
- `s`: Start reading session
- `e`: End reading session  
- `d`: Delete book
- `Escape`: Back to main screen

### Key Bindings (Author Autocomplete)
- Type to filter suggestions
- `↓`/`↑`: Navigate suggestions
- `Enter`: Select suggestion or submit
- `Escape`: Hide suggestions

## Development Notes

### Modular Architecture Benefits
- **Separation of Concerns**: Models, UI, database, and utilities clearly separated
- **Maintainability**: Easy to locate and modify specific components
- **Extensibility**: Simple to add new features, screens, or widgets
- **Reusability**: Components can be imported and reused independently

### Author Autocomplete Implementation
- `DatabaseManager.get_unique_authors()`: Retrieves existing authors
- `AutocompleteInput` widget: Custom Textual widget with dropdown suggestions
- Real-time filtering as user types with substring matching
- Keyboard and mouse navigation support

### Date Input System
The application uses `python-dateutil` for flexible date parsing via `utils/date_utils.py`:
- ISO format: "2023-12-25"
- Natural language: "today", "yesterday", "next monday"
- Various date formats: "Dec 25, 2023", "12/25/2023"

### Database Session Management
Uses context managers for proper session handling in `database/manager.py`:
```python
with self.get_session() as session:
    # Database operations
    session.commit()
```

### Modal Screen Pattern
Modal screens return data via callback functions:
```python
def handle_result(data):
    if data:  # User didn't cancel
        # Process data
        
self.app.push_screen(modal_screen, handle_result)
```

### Custom Widget Development
See `ui/widgets/autocomplete_input.py` for example of creating custom Textual widgets:
- Extend base widgets (Container, Input)
- Handle user events (typing, navigation)
- Custom CSS styling
- Message passing for integration

## Adding New Features

### New Autocomplete Fields
1. Add method to `DatabaseManager` to get unique values
2. Use `AutocompleteInput` widget in relevant screen
3. Pass suggestions list when initializing widget

### New Screen/Modal
1. Create new file in `ui/screens/`
2. Extend `Screen` or `ModalScreen`
3. Add to `ui/screens/__init__.py`
4. Import and use in main app

### New Model
1. Create model file in `models/`
2. Add relationships to existing models if needed
3. Add to `models/__init__.py`
4. Add corresponding methods to `DatabaseManager`

## Testing
No formal test framework is configured. Testing should be done manually by running the application and testing various workflows.

## Dependencies
- `sqlalchemy>=2.0.0`: Database ORM
- `textual>=0.41.0`: TUI framework  
- `python-dateutil>=2.8.0`: Flexible date parsing
- Python 3.13+ (current environment)

## UI Guidelines and Standards

### Core UI Principles
- **Accessibility First**: All UI elements must be keyboard accessible and support screen readers
- **Clear Visual Hierarchy**: Consistent spacing, sizing, and layout across all screens
- **Responsive Design**: UI should work across different terminal sizes
- **Focus Management**: Clear, logical focus order with proper visual indicators

### Layout and Spacing Requirements

#### Input Fields
- **Minimum Height**: All input fields must have height ≥ 3 for visibility
- **Consistent Width**: Use relative sizing (100%) or consistent fixed widths
- **Proper Margins**: Minimum 1 unit spacing between form elements
- **Label Association**: Every input must have a clear, visible label

#### Modal Dialogs
- **Fixed Dimensions**: Use consistent width/height ratios (e.g., width: 80, height: 35)
- **Scrollable Content**: Long forms must have proper scrollable containers
- **Button Placement**: Action buttons should be docked to bottom with consistent spacing
- **Escape Routes**: Always provide clear cancel/escape options

#### Custom Widgets
- **Container Structure**: Use proper Textual containers (Vertical, Horizontal, not raw Container for complex layouts)
- **CSS Layout**: Avoid `dock` properties that can cause layout collapse
- **Explicit Sizing**: Always specify width/height when creating complex layouts
- **Focus Support**: Custom widgets must properly implement focus() method

### Keyboard Navigation Standards

#### Tab Order Requirements
- **Sequential Navigation**: Tab key must move through fields in logical order
- **Reverse Navigation**: Shift+Tab must work for backward movement
- **Skip Empty Regions**: Focus should not get trapped in non-interactive areas
- **Visual Focus**: Currently focused element must be clearly highlighted

#### Modal Screen Navigation
- **Initial Focus**: First interactive element should receive focus on modal open
- **Focus Containment**: Tab navigation should stay within the modal
- **Escape Handling**: ESC key should close modal or hide suggestions consistently
- **Enter Handling**: Enter should submit forms or confirm selections appropriately

### Accessibility Guidelines

#### Screen Reader Support
- **Proper Labels**: All form controls must have associated labels
- **Role Attributes**: Custom widgets should define appropriate ARIA roles
- **State Information**: Dynamic content changes must be announced
- **Error Messages**: Validation errors must be clearly associated with fields

#### Color and Contrast
- **Theme Consistency**: Use Textual's built-in color variables ($primary, $surface, etc.)
- **Error States**: Use $error color for validation failures
- **Success States**: Use $success color for confirmations
- **Focus Indicators**: Ensure focused elements have sufficient contrast

### Testing Checklist for UI Components

#### Keyboard Testing
- [ ] Tab moves through all interactive elements in logical order
- [ ] Shift+Tab works for reverse navigation
- [ ] Arrow keys work appropriately for lists/suggestions
- [ ] Enter key submits forms or confirms selections
- [ ] Escape key cancels operations or hides overlays

#### Layout Testing
- [ ] Component renders correctly in different terminal sizes
- [ ] Text input fields are wide enough for reasonable content
- [ ] Scrolling works when content exceeds container size
- [ ] Buttons are always visible and accessible
- [ ] Modal dialogs center properly and don't overflow

#### Functionality Testing
- [ ] All form fields accept text input correctly
- [ ] Validation messages appear and disappear appropriately
- [ ] Autocomplete suggestions appear and can be selected
- [ ] Modal dialogs can be opened, used, and closed properly
- [ ] Focus returns to appropriate element after modal closure

## Known Issues and Required Fixes

### Add Book Modal Dialog Issues (CRITICAL)

#### Problem Description
The author field in the Add Book modal has significant usability issues:

1. **Field Size Issues**:
   - Author field appears very small/collapsed
   - Text input may not be accepted properly
   - Field may not be visually distinguishable from other elements

2. **Focus Management Problems**:
   - Tab navigation may skip the author field
   - Field may not receive proper focus when selected
   - Keyboard navigation through the form is inconsistent

#### Root Cause Analysis
The issues stem from the `AutocompleteInput` widget implementation in `ui/widgets/autocomplete_input.py`:

1. **CSS Layout Problems**:
   - Uses `dock: top` on internal Input which can cause layout collapse
   - Container has `height: auto` without minimum constraints
   - No explicit width constraints on the Input element

2. **Container Structure Issues**:
   - Uses base `Container` instead of proper layout container (`Vertical`)
   - Complex nested structure interferes with normal focus flow
   - Internal Input widget conflicts with external focus management

3. **Focus Handling Conflicts**:
   - Widget tries to auto-focus on mount, causing conflicts
   - No proper integration with modal screen focus management
   - Tab order not properly defined for complex widget

#### Required Fixes

1. **Fix AutocompleteInput Widget CSS** (`ui/widgets/autocomplete_input.py`):
   ```css
   AutocompleteInput > Input {
       width: 100%;
       height: 3;
       /* Remove dock: top */
   }
   
   AutocompleteInput {
       layout: vertical;
       height: auto;
       min-height: 3;
       width: 100%;
   }
   ```

2. **Add Proper Focus Management** (`ui/screens/add_book.py`):
   ```python
   def on_mount(self) -> None:
       """Set up initial focus when modal opens."""
       self.query_one("#title-input").focus()
   ```

3. **Update Widget Structure** (`ui/widgets/autocomplete_input.py`):
   - Change base class from `Container` to `Vertical`
   - Remove auto-focus from widget initialization
   - Implement proper `can_focus` property

4. **Test and Validate**:
   - Verify all form fields are accessible via Tab key
   - Confirm author field accepts text input properly
   - Check visual consistency across all input fields
   - Test autocomplete functionality still works correctly

### Future UI Development Rules

1. **Always test keyboard navigation** before considering a UI component complete
2. **Use layout containers** (`Vertical`, `Horizontal`) instead of raw `Container` for complex layouts
3. **Avoid `dock` properties** that can cause layout collapse in form fields
4. **Implement proper focus management** in all modal screens
5. **Test with different terminal sizes** to ensure responsive behavior
6. **Follow the testing checklist** above for all new UI components

### Error Handling and Validation

#### Form Validation Standards
- **Real-time Validation**: Provide immediate feedback for invalid inputs
- **Clear Error Messages**: Display specific, actionable error text
- **Error Positioning**: Show errors near relevant fields, not just at top/bottom
- **Error Styling**: Use consistent error styling ($error color, italic text)

#### User Feedback Patterns
- **Success Confirmations**: Show clear success messages after operations
- **Loading States**: Indicate when operations are in progress
- **Destructive Actions**: Always confirm deletion or irreversible operations
- **Cancel Operations**: Always provide clear ways to cancel ongoing actions