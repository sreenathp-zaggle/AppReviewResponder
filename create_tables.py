# create_tables.py

from src.database import engine
from src.repository.models import Base

# This will create all tables defined in models
Base.metadata.create_all(bind=engine)
