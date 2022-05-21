from requests_html import HTMLSession
from time import sleep, time
from datetime import datetime
import re
import psycopg2
from psycopg2 import Error
import sys
import configparser


def get_killboard_html(
    session, killboard_url="https://albiononline.com/killboard", extra_path=""
):
    url = killboard_url + extra_path
    print("Scrapping page with js loaded")
    start = time()

    r = session.get(url)
    r.html.render(sleep=5, timeout=30)
    raw_links = r.html.links
    end = time()

    print(f"Time taken for loading the js: {end - start}")
    return raw_links


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


def create_player_id_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS players.player_id (id VARCHAR(100) UNIQUE, insertion_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);"
        )
        connection.commit()
        print("Created table")
    except (Exception, Error) as error:
        print("Error while creating table", error)
        sys.exit()
    finally:
        cursor.close()


def parse_page(raw_links):
    batch_player_id = []
    batch_guild_id = []
    batch_alliance_id = []
    for item in raw_links:
        player_id = re.search(r"(?<=\/en\/killboard\/player\/).*", item)
        guild_id = re.search(r"(?<=\/en\/killboard\/guild\/).*", item)
        alliance_id = re.search(r"(?<=\/en\/killboard\/alliance\/).*", item)
        if player_id:
            batch_player_id.append(player_id.group())
        if guild_id:
            batch_guild_id.append(guild_id.group())
        if alliance_id:
            batch_alliance_id.append(alliance_id.group())
    return batch_player_id, batch_guild_id, batch_alliance_id


if __name__ == "__main__":
    # TODO configparser module & update config file with API conf
    config = configparser.ConfigParser()
    config.read("config.local.ini")
    db_user = config["DATABASE"]["user"]
    db_password = config["DATABASE"]["password"]
    count_runs = 0
    session = HTMLSession()
    connection = psycopg2.connect(
        user=db_user,
        password=db_password,
        host="127.0.0.1",
        port="5432",
        database="AlbionDB",
    )
    create_player_id_table(connection)
    while True:
        count_runs += 1
        raw_links = get_killboard_html(session=session)
        batch_player_id, batch_guild_id, batch_alliance_id = parse_page(raw_links)

        insert_db(batch_player_id, connection)
        for item in batch_guild_id:
            print(f"Scrapping guild {item}")
            raw_links_guild = get_killboard_html(
                session=session, extra_path=f"/guild/{item}"
            )
            # Could make this recursive and parse the guilds of the guilds etc but might get me kicked out for too many requests
            batch_player_id, batch_guild_id, batch_alliance_id = parse_page(
                raw_links_guild
            )
            insert_db(batch_player_id, connection)

        # Alliance is probably not getting updated as often so we do this scrapping once every two runs
        if count_runs % 2 == 0:
            for item in batch_alliance_id:
                print("Scrapping alliance")
                raw_links_alliance = get_killboard_html(
                    session=session, extra_path=f"/alliance/{item}"
                )
                # Could make this recursive and parse the guilds of the guilds etc but might get me kicked out for too many requests
                batch_player_id, batch_guild_id, batch_alliance_id = parse_page(
                    raw_links_alliance
                )
                insert_db(batch_player_id, connection)

        print("sleeping for 200s")
        sleep(200)
