from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Text
)
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DB_PATH

Base = declarative_base()

class Fiction(Base):
    """SQLAlchemy model for Royal Road fiction data"""
    __tablename__ = "fictions"

    fiction_id   = Column(Integer, primary_key=True)
    title        = Column(String, nullable=False)
    author       = Column(String, nullable=False)

    tags         = Column(Text)     # JSON string of tags list
    pages        = Column(Integer)

    views        = Column(Integer)
    avg_views    = Column(Integer)
    followers    = Column(Integer)
    favorites    = Column(Integer)
    rating_count = Column(Integer)
    avg_rating   = Column(Float)

    status       = Column(String)
    last_updated = Column(String)
    
    # New fields
    fiction_type = Column(String)  # Original, Fanfiction, etc.
    warn_tags    = Column(Text)    # JSON string of warning tags (Gore, etc.)
    content_warnings = Column(Text) # JSON string of content warnings (AI, Mature)

    scraped_at   = Column(String, nullable=False)

    def __repr__(self):
        return f"<Fiction(id={self.fiction_id}, title='{self.title}', author='{self.author}')>"


# Create engine and session factory
engine = create_engine(DB_PATH, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Initialize the database by creating all tables"""
    Base.metadata.create_all(engine)
    print(f"Database initialized at {DB_PATH}")

def get_session():
    """Get a new database session"""
    return SessionLocal()
