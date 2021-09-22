from mysql.connector import MySQLConnection, Error, errorcode


def get_connection(args):
    try:
        connection = MySQLConnection(**args)
    except Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        return connection


if __name__ == '__main__':
    args = {
        'user': 'root',
        'password': 'root',
        'database': 'library',
        'autocommit': True
    }
    connection = get_connection(args)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM room')
    for row in cursor:
        print(row)
    connection.close()