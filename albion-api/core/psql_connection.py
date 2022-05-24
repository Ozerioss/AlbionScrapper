import psycopg2


def open_connection(db_conf):
    connection = psycopg2.connect(
        user=db_conf["user"],
        password=db_conf["password"],
        host=db_conf["host"],
        port=db_conf["port"],
        database=db_conf["db_name"],
    )

    return connection
