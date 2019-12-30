# Creates a decorator to handle the database connection/cursor opening/closing.
# Creates the cursor with RealDictCursor, thus it returns real dictionaries, where the column names are the keys.
import os
import psycopg2
import psycopg2.extras


DATABASE_URL = os.environ['DATABASE_URL']


def get_connection_string():
    # setup connection string
    # to do this, please define these environment variables first
    user_name = 'codecooler'  #os.environ.get('PSQL_USER_NAME')
    password = '123456'  # os.environ.get('PSQL_PASSWORD')
    host = 'localhost'  # os.environ.get('PSQL_HOST')
    database_name = 'qademo'    # os.environ.get('PSQL_DB_NAME')

    env_variables_defined = user_name and password and host and database_name

    if env_variables_defined:
        # this string describes all info for psycopg2 to connect to the database
        return 'postgresql://{user_name}:{password}@{host}/{database_name}'.format(
            user_name=user_name,
            password=password,
            host=host,
            database_name=database_name
        )
    else:
        raise KeyError('Some necessary environment variable(s) are not defined')


def open_database():
    try:
        # connection_string = get_connection_string()
        # connection = psycopg2.connect(connection_string)
        connection = psycopg2.connect(DATABASE_URL, sslmode='require')
        connection.autocommit = True
    except psycopg2.DatabaseError as exception:
        print('Database connection problem')
        raise exception
    return connection


def connection_handler(function):
    def wrapper(*args, **kwargs):
        connection = open_database()
        # we set the cursor_factory parameter to return with a RealDictCursor cursor (cursor which provide dictionaries)
        dict_cur = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        ret_value = function(dict_cur, *args, **kwargs)
        dict_cur.close()
        connection.close()
        return ret_value

    return wrapper
