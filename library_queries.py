any_room_text = 'Любой читальный зал'


def get_books_by_reader(cursor, card_number):
    query = '''
        SELECT b.cipher, b.title, b.author, l.taking_date, b.room_name
        FROM books b, log l
        WHERE b.cipher=l.book_cipher
        AND l.returning_date IS NULL
        AND l.reader_card_number=%s;
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
    if room == any_room_text:
        room = '%'
    query = '''
        SELECT *
        FROM books
        WHERE title LIKE %s
        AND author LIKE %s
        AND room_name LIKE %s
        ORDER BY room_name;
    '''
    cursor.execute(query, (title, author, room))
    return [book for book in cursor]


def get_rooms(cursor):
    query = '''
        SELECT name FROM rooms;
    '''
    cursor.execute(query)
    return [row[0] for row in cursor]


def get_reader_by_book(cursor, cipher):
    query = '''
        SELECT *
        FROM readers
        WHERE card_number 
        IN (SELECT reader_card_number
            FROM log
            WHERE book_cipher=%s
            AND returning_date IS NULL);
    '''
    cursor.execute(query, (cipher, ))
    return [reader for reader in cursor]


def get_reader_by_phone_number(cursor, phone_number):
    query = '''
        SELECT *
        FROM readers
        WHERE phone_number=%s;
    '''
    cursor.execute(query, (phone_number, ))
    return [reader for reader in cursor]


def add_reader(cursor, reader):
    surname, phone_number, card_number, room_name = reader
    if if_room_have_place(cursor, room_name):
        query = '''
            INSERT INTO readers (card_number, surname, phone_number, room_name, registration_date)
            VALUES (%s, %s, %s, %s, current_date());
        '''
        cursor.execute(query, (card_number, surname, phone_number, room_name))


def get_room_capacities(cursor):
    query = '''
        SELECT capacity
        FROM rooms;
    '''
    cursor.execute(query)
    return [capacity for capacity in cursor]


def get_room_sizes(cursor):
    query = '''
        SELECT room_name, count(*) AS size
        FROM readers
        GROUP BY room_name;
    '''
    cursor.execute(query)
    return [room for room in cursor]


def get_rooms_table(cursor):
    query = '''
        SELECT readers.room_name as name, rooms.capacity, count(*)
        FROM readers
        INNER JOIN rooms
        ON readers.room_name=rooms.name
        GROUP BY readers.room_name
        UNION
        SELECT name, capacity, 0
        FROM rooms
        WHERE name not IN (
            SELECT DISTINCT room_name
            FROM readers)
        ORDER BY name;
    '''
    cursor.execute(query)
    return [row for row in cursor]


def if_room_have_place(cursor, room):
    cap_query = '''
        SELECT capacity
        FROM rooms
        WHERE name=%s;
    '''
    size_query = '''
        SELECT count(*)
        FROM readers
        GROUP BY room_name
        HAVING room_name=%s;
    '''
    cursor.execute(cap_query, (room, ))
    result = [row for row in cursor]
    capacity = result[0][0]
    cursor.execute(size_query, (room, ))
    result = [row for row in cursor]
    size = result[0][0]
    return size < capacity


def current_readers_count(cursor):
    query = '''
            SELECT count(*)
            FROM readers;
        '''
    cursor.execute(query)
    return cursor.fetchone()[0]


def readers_count(cursor, year, month):
    query = '''
        SELECT count(*)
        FROM readers
        WHERE registration_date <= LAST_DAY(DATE('%s-%s-01'));
    '''
    cursor.execute(query, (year, month))
    return [row for row in cursor][0][0]


def new_readers_for_month_count(cursor, year, month):
    query = '''
        SELECT count(*)
        FROM readers
        WHERE registration_date
        BETWEEN '%(year)s-%(month)s-01'
        AND LAST_DAY(DATE('%(year)s-%(month)s-01'));
    '''
    cursor.execute(query, {'year': year, 'month': month})
    return [row for row in cursor][0][0]


def books_taken_for_month(cursor, year, month):
    query = '''
      SELECT books.*, count(*)
      FROM log, books
      WHERE log.taking_date
      BETWEEN '%(year)s-%(month)s-01'
      AND LAST_DAY(DATE('%(year)s-%(month)s-01'))
      AND log.book_cipher=books.cipher
      GROUP BY book_cipher;  
    '''
    cursor.execute(query, {'year': year, 'month': month})
    return [book for book in cursor]


def inactive_readers_for_month(cursor, year, month):
    query = '''
        SELECT card_number, surname, phone_number, room_name
        FROM readers
        WHERE card_number NOT IN(
            SELECT reader_card_number
            FROM log
            WHERE taking_date
            BETWEEN '%(year)s-%(month)s-01'
            AND LAST_DAY(DATE('%(year)s-%(month)s-01')))
        AND registration_date <= LAST_DAY(DATE('%(year)s-%(month)s-01'));
    '''
    cursor.execute(query, {'year': year, 'month': month})
    return [reader for reader in cursor]


def get_current_year_and_month(cursor):
    query = '''
        SELECT YEAR(CURDATE()), MONTH(CURDATE());
    '''
    cursor.execute(query)
    return cursor.fetchone()


def get_first_year(cursor):
    query = '''
        SELECT MIN(YEAR(registration_date))
        FROM readers;
    '''
    cursor.execute(query)
    return cursor.fetchone()[0]