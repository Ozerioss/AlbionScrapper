from datetime import datetime
from psycopg2 import Error


def insert_db(batch_player_id, connection):
    current_timestamp = datetime.now().isoformat()
    with connection.cursor() as cursor:
        try:
            print(f"batch players : {len(batch_player_id)}")
            row_count = 0
            for player in batch_player_id:
                cursor.execute(
                    f"INSERT INTO players.player_id(id, insertion_timestamp) VALUES ("
                    f"'{player}', '{current_timestamp}') "
                    f"ON CONFLICT (id) DO NOTHING"
                )
                connection.commit()
                row_count += cursor.rowcount
            print(f"{row_count} records inserted")
        except (Exception, Error) as error:
            print("Error while handling PostgreSQL request", error)


def get_players_id(connection):
    with connection.cursor() as cursor:
        try:
            cursor = connection.cursor()
            select_id = "SELECT id FROM players.player_id ORDER BY kd_ratio desc"
            cursor.execute(select_id)
            player_ids = cursor.fetchall()
            print(f"{len(player_ids)} player ids")
            return player_ids
        except (Exception, Error) as error:
            print("Error while handling PostgreSQL request", error)
            raise


def update_row(player_id, kd_ratio, player_name, kill_fame, death_fame, connection):
    if player_name:
        with connection.cursor() as cursor:
            try:
                update_statement = f"UPDATE players.player_id SET kd_ratio='{kd_ratio}', player_name = '{player_name}', kill_fame='{kill_fame}', death_fame='{death_fame}' WHERE id = '{player_id}'"
                cursor.execute(update_statement)
                connection.commit()
                print(f"Updated {cursor.rowcount} row successfully")
            except (Exception, Error) as error:
                print("Error while handling PostgreSQL request", error)
