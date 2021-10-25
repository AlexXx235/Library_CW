def get_books_by_reader(cursor, card_number):
    query = '''
        SELECT * 
        FROM books 
        WHERE cipher 
            IN (SELECT book_cipher 
                FROM log
                WHERE reader_card_number=%s
        );
    '''
    cursor.execute(query, (card_number, ))
    return [book for book in cursor]


def get_books_by_author(cursor, author):
    query = '''
        SELECT *
        FROM books
        WHERE author=%s;
    '''
    cursor.execute(query, (author, ))
    books = [book for book in cursor]
    return books


def get_books_by_title(cursor, title):
    query = '''
            SELECT *
            FROM books
            WHERE title=%s;
        '''
    cursor.execute(query, (title,))
    books = [book for book in cursor]
    return books


def delete_book(cursor, cipher):
    query = '''
        DELETE 
        FROM books 
        WHERE cipher=%s;
    '''
    cursor.execute(query, (cipher, ))


def change_book_cipher(cursor, old_cipher, new_cipher):
    query = '''
        UPDATE books
        SET cipher=%s
        WHERE cipher=%s;
    '''
    cursor.execute(query, (new_cipher, old_cipher))


def get_book_by_cipher(cursor, cipher):
    query = '''
        SELECT * FROM books WHERE cipher=%s; 
    '''
    cursor.execute(query, (cipher, ))
    return [book for book in cursor]


def filtered_book_search(cursor, title='', author='', room=''):
    title = '%' + title + '%'
    author = '%' + author + '%'
    if room == '':
        room = '%' + room + '%'
    query = '''
        SELECT *
        FROM books
        WHERE title LIKE %s
        AND author LIKE %s
        AND room_name LIKE %s;
    '''
    cursor.execute(query, (title, author, room))
    return [book for book in cursor]


def get_rooms(cursor):
    query = '''
        SELECT name FROM rooms;
    '''
    cursor.execute(query)
    return [row[0] for row in cursor]