import psycopg2
from psycopg2 import Error
import requests
from requests.adapters import HTTPAdapter, Retry
import json
import configparser


def get_players_id(db_user, db_password):
    try:
        connection = psycopg2.connect(
            user=db_user,
            password=db_password,
            host="127.0.0.1",
            port="5432",
            database="AlbionDB",
        )
        cursor = connection.cursor()
        print("PostgreSQL is up")
        select_id = "SELECT id FROM players.player_id ORDER BY kd_ratio desc"
        cursor.execute(select_id)
        player_ids = cursor.fetchall()
        print(f"{len(player_ids)} player ids")
        return player_ids
    except (Exception, Error) as error:
        print("Error while handling PostgreSQL request", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Closed PostgreSQL")


def get_kda(base_url, id, session):
    print("Getting player info for ", id)
    player_url = base_url + f"players/{id}"

    response = session.get(player_url)

    player_name = ""
    kd_ratio = -1
    kill_fame = -1
    death_fame = -1
    try:
        response_json = response.json()
        kill_fame = response_json.get("KillFame")
        death_fame = response_json.get("DeathFame")
        player_name = response_json.get("Name")
        kd_ratio = response_json.get("FameRatio")

        print(f"kd_ratio: {kd_ratio}")
    except json.decoder.JSONDecodeError:
        print("api died I guess")
    print(kill_fame, death_fame)
    return kd_ratio, player_name, kill_fame, death_fame


def update_table(player_id, kd_ratio, player_name, kill_fame, death_fame, connection):
    if player_name:
        try:
            print("PostgreSQL is up")
            cursor = connection.cursor()
            update_statement = f"UPDATE players.player_id SET kd_ratio='{kd_ratio}', player_name = '{player_name}', kill_fame='{kill_fame}', death_fame='{death_fame}' WHERE id = '{player_id}'"
            cursor.execute(update_statement)
            connection.commit()
            print(f"Updated {cursor.rowcount} row successfully")
        except (Exception, Error) as error:
            print("Error while handling PostgreSQL request", error)
        finally:
            cursor.close()


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.local.ini")
    db_user = config["DATABASE"]["user"]
    db_password = config["DATABASE"]["password"]
    albion_api_base_url = "https://gameinfo.albiononline.com/api/gameinfo/"

    connection = psycopg2.connect(
        user=db_user,
        password=db_password,
        host="127.0.0.1",
        port="5432",
        database="AlbionDB",
    )
    session = requests.Session()

    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])

    session.mount("https://", HTTPAdapter(max_retries=retries))
    player_ids = get_players_id(db_user, db_password)
    kd_ratio_batch = []
    offset = 0
    total = 0
    for row in player_ids:
        player_id = row[0]
        kd_ratio, player_name, kill_fame, death_fame = get_kda(
            albion_api_base_url, player_id, session
        )
        offset += 1
        total += 1
        print("Number of total players updated: ", total)
        update_table(
            player_id, kd_ratio, player_name, kill_fame, death_fame, connection
        )
    connection.close()
    print("Closed Postgresql")
    # if offset >= 100:
    #     print(f"Updating {offset} rows")
    #     update_table(kd_ratio_batch, player_id)
    #     print("total rows updated so far : ", total)
    #     offset = 0
