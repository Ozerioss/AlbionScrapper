from psycopg2 import Error


def create_player_id_table(connection):
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS players.player_id ("
                f"id VARCHAR(100) UNIQUE, "
                f"insertion_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                f"kd_ratio            double precision,"
                f"player_name         varchar(125),"
                f"kill_fame           double precision,"
                f"death_fame          double precision"
                f"); "
            )
            connection.commit()
            print("Created table")
        except (Exception, Error) as error:
            print("Error while creating table", error)
            raise
