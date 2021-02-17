import sqlite3
from datetime import datetime


db_file = r"db.sqlite"


def manage_infractions(message, operation):
    """
    Executes insert, update and delete for infractions table
    Operation number is needed for the function.

    # Returns

    True {bool} : For operation 2

    show_infractions {list} : For operation 3, list containing the infractions
                              data for the user
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    curr_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    #  to ensure the space between date and time is not causing issues,
    #  inserting quotes
    curr_time = '"{}"'.format(curr_time)

    if operation == 1:  # insert/update table, add infractions
        cursor.execute(
            f"SELECT * FROM infractions WHERE user_id={message.author.id}")

        if len(cursor.fetchall()) != 0:  # if user found in table

            cursor.execute(
                f"UPDATE infractions SET infractions = infractions + 1, last_triggered = {curr_time} WHERE user_id={message.author.id}"

            )
        else:

            cursor.execute(
                f"INSERT INTO infractions VALUES ({message.author.id}, 1, {curr_time})"
            )

        conn.commit()
        conn.close()

    elif operation == 2:  # delete from table, remove infractions

        cursor.execute(f"DELETE FROM infractions WHERE user_id={message}")
        conn.commit()
        conn.close()
        return True

    elif operation == 3:  # select from table, show infractions

        cursor.execute(f"SELECT * FROM infractions \
                             WHERE user_id={message}")

        show_infractions = cursor.fetchall()
        conn.commit()
        conn.close()
        return show_infractions


def manage_muted_users(message, operation):
    """
    Executes insert, update and delete for muted_users table
    Operation number is needed for the function.

    # Returns

    True {bool} : For operation 2

    show_muted_users {list} : For operation 3, list containing the infractions
                              data for the user
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    curr_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # to ensure the space between date and time is not causing issues, inserting quotes
    curr_time = '"{}"'.format(curr_time)

    if operation == 1:  # insert table, add muted_users

        if isinstance(message, int):  # if message is the user_id
            cursor.execute(
                f"SELECT * FROM muted_users WHERE user_id={message}")
        else:
            cursor.execute(
                f"SELECT * FROM muted_users WHERE user_id={message.author.id}")

        if len(cursor.fetchall()) == 0:  # if user not found in the table
            if isinstance(message, int):  # if message is the user_id
                cursor.execute(
                    f"INSERT INTO muted_users VALUES ({message}, {curr_time})")

            else:
                cursor.execute(
                    f"INSERT INTO muted_users VALUES ({message.author.id}, {curr_time})")

        conn.commit()
        conn.close()
        return True

    elif operation == 2:  # delete from table, remove muted_users

        cursor.execute(
            f"DELETE FROM muted_users WHERE user_id={message}")
        conn.commit()
        conn.close()
        return True

    elif operation == 3:  # select from table, show muted_users

        cursor.execute(f"SELECT * FROM muted_users \
                             WHERE user_id={message}")

        show_muted_users = cursor.fetchall()
        conn.commit()
        conn.close()
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
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM infractions")

    show_infractions = cursor.fetchall()
    conn.commit()
    conn.close()
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
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM muted_users")

    show_muted_users = cursor.fetchall()
    conn.commit()
    conn.close()
    return show_muted_users
