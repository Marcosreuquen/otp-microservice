from config import settings
DATABASE_URL = settings.DATABASE_URL
from .tables import User, AuthService, Auth, App, UserAppLink
from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager

class DB:
    def __init__(self, database_url: str = None):
        self.database_url = database_url
        self.engine = create_engine(self.database_url)

    def create_db_and_tables(self):
        """Crea las tablas definidas en los modelos de SQLModel."""
        SQLModel.metadata.create_all(self.engine)

    def init_db(self):
        print("Creating tables on the database...")
        self.create_db_and_tables()
        print("Tables created successfully or already exist.")

    @contextmanager
    def session(self):
        """Proporciona una sesión de base de datos y maneja el cierre de la sesión."""
        session = Session(self.engine)
        try:
            yield session
        finally:
            session.close()

# global instance of DB
db = DB(DATABASE_URL)

def get_session():
    # Creates a new session for each request.
    with db.session() as session:
        yield session
