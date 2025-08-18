"""
Database Base Configuration
Shared SQLAlchemy base class for all database models.
"""

from sqlalchemy.ext.declarative import declarative_base

# Create the base class for all database models
Base = declarative_base()
