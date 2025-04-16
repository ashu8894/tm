# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://truckdb_user:4L1V94qsWljZLBIma4JwLP78puYY9JBQ@dpg-cvvr8cuuk2gs73djt0t0-a.virginia-postgres.render.com/truckdb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
