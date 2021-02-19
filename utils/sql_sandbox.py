from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# create an engine which is an object that is used
# to manage the connection to the database
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

# Execute operations
#! Do not use operations on the infractions & muted_users table,
#! since they are being used in production

db.execute(
    "CREATE TABLE infractions (user_id bigint PRIMARY KEY, infractions int, last_triggered TEXT);")

db.execute(
    "CREATE TABLE muted_users (user_id bigint PRIMARY KEY, last_triggered TEXT);")

db.execute(
    "INSERT INTO infractions VALUES(8977373771213829,1,'2021-02-17 15:21:20');")

result = db.execute("SELECT * FROM infractions;")
result = result.cursor.fetchall()  # To get a list from the select statement

db.commit()
db.close()
