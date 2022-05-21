import requests
from main import insert_db
from requests.adapters import HTTPAdapter, Retry
import json
import psycopg2
from config import read_config

def get_battle_ids(base_url, session, connection):
    for offset in range(0, 9949, 51):
        print(f"Handling battles at offset : {offset}")
        battles_url = base_url + f"battles?range=month&offset={offset}&limit=51"
        response = session.get(battles_url)

        try:
            response_json = response.json()
            for item in response_json:
                batch_player_id = item.get("players").keys()
                insert_db(batch_player_id, connection)

        except json.decoder.JSONDecodeError:
            print("api died I guess")


def get_guild_members(base_url, session, connection, guild_id):
    guild_members_url = base_url + f"guilds/{guild_id}/members"
    response = session.get(guild_members_url)
    try:
        response_json = response.json()
        for item in response_json:
            batch_player_id = item.get("Id")
            print("from guilds thingy ", batch_player_id)
    except json.decoder.JSONDecodeError:
        print("api died I guess")


# def get_events(base_url, session, connection):
#     for offset in range(0, 9949, 51):


#         print(f"Handling battles at offset : {offset}")
#         battles_url = base_url + f" ?range=day&offset={offset}&limit=51"
#         response = session.get(battles_url)

#         try:
#             response_json = response.json()
#             for item in response_json:
#                 batch_player_id = item.get('players').keys()
#                 insert_db(batch_player_id, connection)

#         except json.decoder.JSONDecodeError:
#             print("api died I guess")


if __name__ == "__main__":
    config = read_config()
    db_user = config["DATABASE"]["user"]
    db_password = config["DATABASE"]["password"]

    albion_api_base_url = "https://gameinfo.albiononline.com/api/gameinfo/"
    session = requests.Session()

    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])

    session.mount("http://", HTTPAdapter(max_retries=retries))

    connection = psycopg2.connect(
        user=db_user,
        password=db_password,
        host="127.0.0.1",
        port="5432",
        database="AlbionDB",
    )

    get_battle_ids(albion_api_base_url, session, connection)
    connection.close()
