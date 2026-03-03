import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rpg.db")

# Railway usa 'postgres://' mas SQLAlchemy precisa de 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)