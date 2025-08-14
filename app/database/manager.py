"""
Database Manager Alias for ETL System
Provides compatibility with the ETL components by aliasing the existing database manager.
"""

# Import the existing DatabaseManager from the main data module
from ..data.database import DatabaseManager

# Export the DatabaseManager for ETL components
__all__ = ["DatabaseManager"]
