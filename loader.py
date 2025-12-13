"""
Database loading functions.
Handles batch insertion and upsert operations.
"""
from sqlalchemy.dialects.sqlite import insert
from db import Fiction


def upsert_fictions(session, rows):
    """
    Insert or update fiction records in the database.
    Uses SQLite's INSERT OR REPLACE functionality.
    
    Args:
        session: SQLAlchemy session
        rows (list): List of dictionaries containing fiction data
        
    Returns:
        None
    """
    if not rows:
        return
    
    # Create insert statement
    stmt = insert(Fiction).values(rows)
    
    # Get all columns except the primary key for updating
    update_cols = {
        c.name: c 
        for c in stmt.excluded 
        if c.name != "fiction_id"
    }

    # Create upsert statement (insert or update on conflict)
    stmt = stmt.on_conflict_do_update(
        index_elements=["fiction_id"],
        set_=update_cols
    )

    session.execute(stmt)
    session.commit()


def insert_fictions(session, rows):
    """
    Simple batch insert of fiction records.
    Use this if you're sure there are no duplicates.
    
    Args:
        session: SQLAlchemy session
        rows (list): List of dictionaries containing fiction data
        
    Returns:
        None
    """
    if not rows:
        return
    
    session.bulk_insert_mappings(Fiction, rows)
    session.commit()
