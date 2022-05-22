from datetime import datetime
from psycopg2 import Error


def insert_db(batch_player_id, connection):
    current_timestamp = datetime.now().isoformat()
    try:
        cursor = connection.cursor()
        print(f"batch players : {len(batch_player_id)}")
        row_count = 0
        for player in batch_player_id:
            cursor.execute(
                f"INSERT INTO players.player_id(id, insertion_timestamp) VALUES ('{player}', '{current_timestamp}') ON CONFLICT (id) DO NOTHING"
            )
            connection.commit()
            row_count += cursor.rowcount
        print(f"{row_count} records inserted")
    except (Exception, Error) as error:
        print("Error while handling PostgreSQL request", error)
    finally:
        cursor.close()
