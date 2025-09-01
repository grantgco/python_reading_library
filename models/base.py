"""
SQLAlchemy base configuration for the book library application.
"""

from sqlalchemy.orm import declarative_base

# Create the base class for our database models
Base = declarative_base()