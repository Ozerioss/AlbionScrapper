from requests_html import HTMLSession
from pprint import pprint
from time import time
from datetime import datetime
import re
import psycopg2
from psycopg2 import Error



def get_killboard_html():
    start = time()
    
    killboard_url = "https://albiononline.com/killboard"
    session = HTMLSession()

    r = session.get(killboard_url)
    r.html.render(sleep = 3, timeout = 20)
    raw_links = r.html.links
    end = time()
    with open('rendered.html', 'w', encoding = 'utf-8') as file:
        file.write(str(raw_links))
    
    print(f"Time taken for loading the js: {end - start}")
    return raw_links
    


def insert_db(batch_player_id):
    current_timestamp = datetime.now().strftime("%H:%M:%S")

    try:
        connection = psycopg2.connect(user="postgres", password="", host="127.0.0.1", port="5432", database="AlbionDB")
        cursor = connection.cursor()

        print("PostgreSQL is up")
        print(connection.get_dsn_parameters(), "\n")
        for player in batch_player_id:
            cursor.execute(f"INSERT INTO players.player_id(id, inserted_timestamp) VALUES ('{player}', '{current_timestamp}')")
        connection.commit()
        print(f"{len(batch_player_id)} records inserted")
    except (Exception, Error) as error:
        print("Error while handling PostgreSQL request", error)
    finally:
        if(connection):
            cursor.close()
            connection.close()
            print("Closed PostgreSQL")
    



if __name__ == "__main__":
    raw_links = get_killboard_html()
    batch_player_id = []
    for item in raw_links:
        player_id = re.search(r"(?<=\/en\/killboard\/player\/).*", item)
        if player_id:
            batch_player_id.append(player_id.group())
    insert_db(batch_player_id)