from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL='postgresql://event_zyfw_user:D1e2bhMQayVQniMxkffXdkP3bS0mdInB@dpg-d6el5f3uibrs73dfco5g-a.oregon-postgres.render.com/event_zyfw'

engine=create_engine(DATABASE_URL)

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base=declarative_base()

def get_db():
    db=SessionLocal()
    try: 
        yield db
    finally:
        db.close()

