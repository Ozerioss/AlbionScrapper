import psycopg2


def open_connection(db_conf):
    # TODO add host & port to conf
    connection = psycopg2.connect(
        user=db_conf["user"],
        password=db_conf["password"],
        host="127.0.0.1",
        port="5432",
        database=db_conf["db_name"],
    )

    return connection
