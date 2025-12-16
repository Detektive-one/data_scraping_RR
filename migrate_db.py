"""
Simple migration script to add new columns to the SQLite database.
Adds: fiction_type, warn_tags, content_warnings
"""
from sqlalchemy import create_engine, text
from config import DB_PATH

def migrate():
    print(f"Migrating database at {DB_PATH}...")
    
    # Extract path from sqlite:///path
    db_file = DB_PATH.replace("sqlite:///", "")
    engine = create_engine(DB_PATH)
    
    with engine.connect() as conn:
        # Check existing columns
        result = conn.execute(text("PRAGMA table_info(fictions)"))
        columns = [row[1] for row in result.fetchall()]
        
        new_columns = [
            ("fiction_type", "VARCHAR"),
            ("warn_tags", "TEXT"),
            ("content_warnings", "TEXT")
        ]
        
        for col_name, col_type in new_columns:
            if col_name not in columns:
                print(f"Adding column: {col_name} ({col_type})")
                try:
                    conn.execute(text(f"ALTER TABLE fictions ADD COLUMN {col_name} {col_type}"))
                    print(f"✓ Added {col_name}")
                except Exception as e:
                    print(f"✗ Failed to add {col_name}: {e}")
            else:
                print(f"Column {col_name} already exists")
                
        conn.commit()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
