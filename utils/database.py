from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# create an engine which is an object that is used
# to manage the connection to the database
engine = create_engine(DATABASE_URL)


def manage_infractions(message, operation):
    """
    Executes insert, update and delete for infractions table
    Operation number is needed for the function.

    # Returns

    True {bool} : For operation 2

    show_infractions {list} : For operation 3, list containing the infractions
                              data for the user
    """

    # create a scoped session
    db = scoped_session(sessionmaker(bind=engine))
    curr_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    if operation == 1:  # insert/update table, add infractions
        result = db.execute(
            f"SELECT * FROM infractions WHERE user_id={message.author.id}")

        if len(result.cursor.fetchall()) != 0:  # if user found in table

            db.execute(
                f"UPDATE infractions SET infractions = infractions + 1, last_triggered = '{curr_time}' WHERE user_id={message.author.id}"

            )
        else:

            db.execute(
                f"INSERT INTO infractions VALUES ({message.author.id}, 1, '{curr_time}')"
            )

        db.commit()
        db.close()

    elif operation == 2:  # delete from table, remove infractions

        db.execute(f"DELETE FROM infractions WHERE user_id={message}")
        db.commit()
        db.close()
        return True

    elif operation == 3:  # select from table, show infractions

        result = db.execute(f"SELECT * FROM infractions \
                             WHERE user_id={message}")

        show_infractions = result.cursor.fetchall()
        db.commit()
        db.close()
        return show_infractions


def manage_muted_users(member, operation, time_out=None):
    """
    Executes insert, update and delete for muted_users table
    Operation number is needed for the function.

    # Returns

    True {bool} : For operation 2

    show_muted_users {list} : For operation 3, list containing the infractions
                              data for the user
    """

    # create a scoped session
    db = scoped_session(sessionmaker(bind=engine))
    curr_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    if operation == 1:  # insert table, add muted_users

        if isinstance(member, int):
            result = db.execute(
                f"SELECT * FROM muted_users WHERE user_id={member}")

        else:
            result = db.execute(
                f"SELECT * FROM muted_users WHERE user_id={member.id}")

        if len(result.cursor.fetchall()) == 0:  # if user not found in the table
            if isinstance(member, int):  # if message is the user_id
                db.execute(
                    f"INSERT INTO muted_users VALUES ({member}, {time_out}, '{curr_time}')")

            else:
                db.execute(
                    f"INSERT INTO muted_users VALUES ({member.id}, {time_out}, '{curr_time}')")

        db.commit()
        db.close()
        return True

    elif operation == 2:  # delete from table, remove muted_users

        if isinstance(member, int):  # if message is the user_id
            db.execute(
                f"DELETE FROM muted_users WHERE user_id={member}")
        else:
            db.execute(
                f"DELETE FROM muted_users WHERE user_id={member.id}")

        db.commit()
        db.close()
        return True

    elif operation == 3:  # select from table, show muted_users
        if isinstance(member, int):  # if message is the user_id
            result = db.execute(f"SELECT * FROM muted_users \
                                WHERE user_id={member}")
        else:
            result = db.execute(f"SELECT * FROM muted_users \
                                WHERE user_id={member.id}")

        show_muted_users = result.cursor.fetchall()
        db.commit()
        db.close()
        return show_muted_users


def check_infractions():
    """
    Executes insert, update and delete for muted_users table
    Operation number is needed for the function.

    # Returns

    True {bool} : For operation 2

    show_muted_users {list} : For operation 3, list containing the infractions
                              data for the user
    """

    # create a scoped session
    db = scoped_session(sessionmaker(bind=engine))

    result = db.execute("SELECT * FROM infractions")

    show_infractions = result.cursor.fetchall()
    db.commit()
    db.close()
    return show_infractions


def check_muted_users():
    """
    Executes insert, update and delete for muted_users table
    Operation number is needed for the function.

    # Returns

    True {bool} : For operation 2

    show_muted_users {list} : For operation 3, list containing the infractions
                              data for the user
    """

    db = scoped_session(sessionmaker(bind=engine))

    result = db.execute("SELECT * FROM muted_users")

    show_muted_users = result.cursor.fetchall()
    db.commit()
    db.close()
    return show_muted_users
