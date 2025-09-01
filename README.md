# Personal Book Library Tracker

A modern, terminal-based book library management system built with Python, SQLAlchemy, and Textual. Track your books, reading sessions, and notes with an intuitive TUI interface featuring author autocomplete.

## ✨ Features

- **📚 Book Management**: Add, view, edit, and delete books with detailed metadata
- **🔍 Author Autocomplete**: Smart suggestions based on your existing library
- **📖 Reading Sessions**: Track when you start and finish books
- **📝 Notes System**: Add reviews, highlights, thoughts, and quotes
- **🗓️ Flexible Date Input**: Natural language date parsing ("today", "last monday", etc.)
- **⌨️ Keyboard Navigation**: Full keyboard control for efficient usage
- **🎨 Clean TUI**: Modern terminal interface powered by Textual

## 🚀 Quick Start

### Installation

```bash
# Clone or download the library folder
cd library

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

```bash
python3 main.py
```

The application will automatically create a SQLite database (`book_library.db`) on first run.

## 🎮 Usage

### Main Screen
- **`a`**: Add new book (with author autocomplete)
- **`Enter`**: View selected book details
- **`r`**: Refresh book list
- **`q`**: Quit application

### Book Detail Screen
- **`s`**: Start reading session
- **`e`**: End reading session
- **`n`**: Add note
- **`d`**: Delete book
- **`Escape`**: Return to main screen

### Author Autocomplete
- Type to see matching authors from your library
- **`↓`/`↑`**: Navigate suggestions
- **`Enter`**: Select suggestion
- **`Escape`**: Hide suggestions

### Date Input
Enter dates in various formats:
- `today`, `yesterday`, `tomorrow`
- `2024-01-15`, `01/15/2024`
- `Jan 15, 2024`, `last monday`

## 🏗️ Architecture

The application follows a clean modular architecture:

```
library/
├── models/          # Database models (Book, ReadingSession, Note)
├── database/        # Database management and operations
├── ui/              # User interface components
│   ├── screens/     # Individual screens (main, detail, modals)
│   ├── widgets/     # Custom widgets (autocomplete input)
│   └── styles/      # CSS styling
├── utils/           # Utility functions (date parsing, etc.)
├── main.py          # Application entry point
└── requirements.txt # Dependencies
```

## 🔧 Development

### Adding New Features

**New Autocomplete Field:**
1. Add method to `DatabaseManager` to get unique values
2. Use `AutocompleteInput` widget in the relevant screen
3. Pass suggestions list when initializing

**New Screen:**
1. Create file in `ui/screens/`
2. Extend `Screen` or `ModalScreen`  
3. Add to `__init__.py` and import in main app

**New Database Model:**
1. Create model file in `models/`
2. Add relationships if needed
3. Update `DatabaseManager` with corresponding methods

### Code Style
- Follow the existing modular pattern
- Use type hints where possible
- Add docstrings for classes and methods
- Keep UI logic separate from business logic

## 📋 Requirements

- Python 3.8+
- SQLAlchemy 2.0+
- Textual 0.41.0+
- python-dateutil 2.8.0+

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📚 Built With

- [Textual](https://textual.textualize.io/) - Modern TUI framework
- [SQLAlchemy](https://sqlalchemy.org/) - Database ORM  
- [python-dateutil](https://dateutil.readthedocs.io/) - Date parsing
- [SQLite](https://sqlite.org/) - Database engine