import json
import os

from sqlmodel import Session, SQLModel, create_engine
from app.models.tables import App, User, AuthService, Auth
from config import settings
from app.utils.logger import Logger
from app.lib.otp import generate_secret

DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
file_path = os.path.join(os.path.dirname(__file__), "seed_data.json")


from sqlmodel import SQLModel
from sqlalchemy import MetaData

def drop_database():
    with Session(engine) as session:
        connection = session.connection()
        Logger.info("Dropping database...")
        Logger.info("Setting session_replication_role to 'replica'.")
        connection.exec_driver_sql("SET session_replication_role = 'replica';")
        Logger.info("Dropping tables...")
        SQLModel.metadata.drop_all(connection)
        Logger.info("Setting session_replication_role to 'origin'.")
        connection.exec_driver_sql("SET session_replication_role = 'origin';")
        session.commit()
        Logger.info("Database dropped successfully.")



def seed_data():
    Logger.info("Seeding database...")
    with Session(engine) as session:
        Logger.info("Getting data...")
        with open(file_path) as file:
            data = json.load(file)
            Logger.info("Data loaded successfully.")

            Logger.info("Adding users...")
            Logger.info("Users: ", len(data["users"]))
            for user in data["users"]:
                Logger.info("Adding user: ", user["username"])
                session.add(User(**user))
            Logger.info("Users added successfully.")
            session.commit()
            Logger.info("Adding apps...")
            for app in data["apps"]:
                Logger.info("Adding app: ", app["name"])
                session.add(App(**app))
            Logger.info("Apps added successfully.")

            Logger.info("Adding auth services...")
            for auth in data["auth"]:
                Logger.info("Adding auth service: ", auth["id"])
                session.add(Auth(**auth))
            Logger.info("Auth services added successfully.")

            Logger.info("Adding services...")
            for service in data["services"]:
                Logger.info("Adding service: ", service["id"])
                service["otp_secret"] = generate_secret()
                session.add(AuthService(**service))
            Logger.info("Services added successfully.")

        session.commit()
