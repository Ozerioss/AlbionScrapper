import json
from config import read_config
from core.psql_connection import open_connection
from core.session import get_session
from database.operations import get_players_id, update_row


def get_kda(base_url, player_id, session):
    print("Getting player info for ", player_id)
    player_url = base_url + f"players/{player_id}"

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


def run_mass_update(connection, session, base_url):
    player_ids = get_players_id(connection)
    total = 0
    for row in player_ids:
        player_id = row[0]
        kd_ratio, player_name, kill_fame, death_fame = get_kda(
            base_url, player_id, session
        )
        total += 1
        print("Number of total players updated: ", total)
        update_row(player_id, kd_ratio, player_name, kill_fame, death_fame, connection)


if __name__ == "__main__":
    config = read_config()
    db_conf = config["DATABASE"]
    albion_api_base_url = config["API"]["url"]

    psql_connection = open_connection(db_conf)
    s = get_session()

    run_mass_update(psql_connection, s, albion_api_base_url)

    psql_connection.close()
    print("Closed Postgresql")
