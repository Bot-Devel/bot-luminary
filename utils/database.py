import sqlite3

db_file = r"db.sqlite"


def manage_infractions(message, operation):
    """
    Executes sql commands for different operations.
    Operation number is needed for the function.

    # Returns
        True {bool} : For operation 2
        show_infractions {list} : For operation 3, list containing the infractions data for the user
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    if operation == 1:  # insert into table, add infractions
        cursor.execute(
            f"SELECT * FROM moderation WHERE user_id={message.author.id}")

        if len(cursor.fetchall()) != 0:  # if user found in table

            cursor.execute(
                f"UPDATE moderation SET infractions = infractions + 1 WHERE user_id={message.author.id}"
            )
        else:
            cursor.execute(
                f"INSERT INTO moderation VALUES ({message.author.id}, 1)"
            )

        conn.commit()
        conn.close()

    elif operation == 2:  # delete from table, remove infractions

        cursor.execute(f"DELETE FROM moderation WHERE user_id={message}")
        conn.commit()
        conn.close()
        return True

    elif operation == 3:  # select from table, add infractions

        cursor.execute(f"SELECT * FROM moderation \
                             WHERE user_id={message}")

        show_infractions = cursor.fetchall()
        conn.commit()
        conn.close()
        return show_infractions
