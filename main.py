#!/usr/bin/env python3
"""
Personal Book Library Tracker
A SQLite-based textual UI application for tracking books, reading sessions, and notes.

Entry point for the modularized book library application.
"""

from ui import LibraryApp


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