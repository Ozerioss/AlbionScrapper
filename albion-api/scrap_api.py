from web_scrapper import insert_db
import json
from config import read_config
from core.psql_connection import open_connection
from core.session import get_session


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
    db_conf = config["DATABASE"]

    albion_api_base_url = "https://gameinfo.albiononline.com/api/gameinfo/"
    session = get_session()

    connection = open_connection(db_conf)

    get_battle_ids(albion_api_base_url, session, connection)
    connection.close()
