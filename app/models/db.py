from config import settings
DATABASE_URL = settings.DATABASE_URL
from .tables import User, AuthService, Auth, App
from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager
from app.utils.logger import Logger

class DB:
    def __init__(self, database_url: str = None):
        self.database_url = database_url
        self.engine = create_engine(self.database_url)

    def create_db_and_tables(self):
        SQLModel.metadata.create_all(self.engine)

    def init_db(self):
        Logger.info("Creating tables on the database.")
        self.create_db_and_tables()
        Logger.info("Tables created successfully or already exist.")

    @contextmanager
    def session(self):
        Logger.info("Creating session.")
        session = Session(self.engine)
        try:
            yield session
        finally:
            Logger.info("Closing session.")
            session.close()

# global instance of DB
db = DB(DATABASE_URL)

def get_session():
    # Creates a new session for each request.
    with db.session() as session:
        yield session
