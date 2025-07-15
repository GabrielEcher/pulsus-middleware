from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()

user = os.getenv("DB_USER")
pwd = os.getenv("DB_PASSWORD")

oracle_engine = create_engine(f"oracle+oracledb://{user}:{pwd}@10.0.0.22/orcl2")

Session = sessionmaker(bind=oracle_engine)