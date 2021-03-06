any_room_text = 'Любой читальный зал'


def start_transaction(cursor):
    cursor.execute('START TRANSACTION;')


def commit(cursor):
    cursor.execute('COMMIT;')


def rollback(cursor):
    cursor.execute('ROLLBACK;')


def get_role(cursor):
    cursor.execute('SELECT CURRENT_ROLE();')
    return cursor.fetchone()[0]


def add_book(cursor, cipher, title, author):
    query = '''
        INSERT INTO books
        VALUES (%s, %s, %s);
    '''
    cursor.execute(query, (cipher, title, author))


def add_book_copy(cursor, inv_number, cipher, room_name, release_year):
    query = '''
        INSERT INTO book_copies
        VALUES (%s, %s, %s, %s);
    '''
    cursor.execute(query, (inv_number, cipher, room_name, release_year))


def get_count_of_book_copies(cursor, cipher):
    query = '''
        SELECT count(*)
        FROM book_copies
        WHERE cipher=%s;
    '''
    cursor.execute(query, (cipher, ))
    return cursor.fetchone()[0]


def get_copy_cipher(cursor, inv_number):
    query = '''
        SELECT cipher
        FROM book_copies
        WHERE inv_number = %s;
    '''
    cursor.execute(query, (inv_number, ))
    return cursor.fetchone()[0]


def delete_book(cursor, cipher):
    query = '''
        DELETE 
        FROM books 
        WHERE cipher=%s;
    '''
    cursor.execute(query, (cipher, ))


def get_reader_holding_book_copy(cursor, inv_number):
    query = '''
        SELECT *
        FROM readers
        WHERE card_number IN(
            SELECT reader_card_number 
            FROM log
            WHERE book_copy_inv_number=%s);
    '''
    cursor.execute(query, (inv_number, ))
    return cursor.fetchone()


def delete_book_copy(cursor, inv_number):
    query = '''
        DELETE 
        FROM book_copies
        WHERE inv_number=%s;
    '''
    cursor.execute(query, (inv_number, ))


def change_book_cipher(cursor, old_cipher, new_cipher):
    query = '''
        UPDATE books
        SET cipher = %s
        WHERE cipher = %s;
    '''
    cursor.execute(query, (new_cipher, old_cipher))


def get_empty_slots_count_by_room(cursor, room_name):
    query = '''
        SELECT (rooms.capacity - count(*))
        FROM rooms, readers
        WHERE rooms.name=%s
        AND readers.room_name=%s
        GROUP BY rooms.name; 
    '''
    cursor.execute(query, (room_name, room_name))
    return cursor.fetchone()[0]


def add_reader(cursor, card_number, name, surname, phone_number, room_name):
    query = '''
        INSERT INTO readers
        VALUES(%s, %s, %s, %s, %s, CURDATE());
    '''
    cursor.execute(query, (card_number, name, surname, phone_number, room_name))


def get_book_copies_by_reader(cursor, card_number):
    query = '''
        WITH numbers AS
            (SELECT book_copy_inv_number AS num, taking_date
             FROM log 
             WHERE reader_card_number = %s
             AND returning_date IS NULL),
             pairs AS
            (SELECT bc.cipher, bc.inv_number, numbers.taking_date
             FROM book_copies bc, numbers
             WHERE bc.inv_number = numbers.num)
        SELECT b.*, bc.inv_number, bc.room_name, bc.release_year, pairs.taking_date
        FROM books b, book_copies bc, pairs
        WHERE b.cipher = pairs.cipher
        AND bc.inv_number = pairs.inv_number;
    '''
    cursor.execute(query, (card_number, ))
    return cursor.fetchall()


def delete_reader(cursor, card_number):
    query = '''
        DELETE FROM readers
        WHERE card_number = %s;
    '''
    cursor.execute(query, (card_number, ))


def loan_book(cursor, card_number, inv_number):
    query = '''
        INSERT INTO log (reader_card_number, book_copy_inv_number, taking_date, returning_date)
        VALUES (%s, %s, CURDATE(), NULL);
    '''
    cursor.execute(query, (card_number, inv_number))


def return_book(cursor, inv_number):
    query = '''
        UPDATE log
        SET returning_date = CURDATE()
        WHERE book_copy_inv_number = %s
        AND returning_date IS NULL;
    '''
    cursor.execute(query, (inv_number, ))


def get_book_by_cipher_and_room(cursor, cipher, room):
    query = '''
        SELECT b.*, count(*)
        FROM books b, book_copies bc
        WHERE b.cipher = %s
        AND b.cipher = bc.cipher
        AND bc.room_name LIKE %s
        GROUP BY bc.cipher; 
    '''
    cursor.execute(query, (cipher, room))
    return cursor.fetchall()


def filtered_book_search(cursor, cipher='', title='', author='', room=''):
    if room == any_room_text:
        room = '%'
    if cipher != '':
        return get_book_by_cipher_and_room(cursor, cipher, room)
    title = '%' + title + '%'
    author = '%' + author + '%'
    query = '''
        SELECT b.*, count(*)
        FROM books b, book_copies bc
        WHERE b.cipher = bc.cipher
        AND b.title LIKE %s
        AND b.author LIKE %s
        AND bc.room_name LIKE %s
        GROUP BY bc.cipher;
    '''
    cursor.execute(query, (title, author, room))
    return cursor.fetchall()


def filtered_available_book_search(cursor, cipher='', title='', author='', room=''):
    if room == any_room_text:
        room = '%'
    if cipher != '':
        return get_book_by_cipher_and_room(cursor, cipher, room)
    title = '%' + title + '%'
    author = '%' + author + '%'
    query = '''
        SELECT b.*, count(*)
        FROM books b, book_copies bc
        WHERE bc.inv_number NOT IN 
            (SELECT book_copy_inv_number
             FROM log
             WHERE returning_date IS NULL) 
        AND b.cipher = bc.cipher
        AND b.title LIKE %s
        AND b.author LIKE %s
        AND bc.room_name LIKE %s
        GROUP BY bc.cipher;
    '''
    cursor.execute(query, (title, author, room))
    return cursor.fetchall()


def book_copy_search_by_inv_number(cursor, inv_number):
    query = '''
        SELECT *
        FROM book_copies
        WHERE inv_number = %s;
    '''
    cursor.execute(query, (inv_number, ))
    return cursor.fetchone()


def filtered_book_copy_search(cursor, cipher='', year_from=0, year_till=-1, room_name='%'):
    if cipher == '':
        cipher = '%'
    if year_till == -1:
        year_till = 'YEAR(CURDATE())'
    if room_name == any_room_text:
        room_name = '%'
    query = '''
        SELECT bc.cipher, bc.inv_number, bc.release_year, bc.room_name, exists
            (SELECT *
             FROM log
             WHERE book_copy_inv_number = bc.inv_number
             AND returning_date IS NULL) AS loaned
        FROM book_copies bc
        WHERE bc.cipher LIKE %s
        AND bc.release_year BETWEEN %s AND %s
        AND room_name LIKE %s;
    '''
    cursor.execute(query, (cipher, year_from, year_till, room_name))
    return cursor.fetchall()


def get_rooms(cursor):
    query = '''
        SELECT name FROM rooms;
    '''
    cursor.execute(query)
    return [row[0] for row in cursor]


def get_reader_by_copy_number(cursor, inv_number):
    query = '''
        SELECT card_number,
        CONCAT(surname, ' ', SUBSTRING(name, 1, 1), '.'),
        phone_number,
        room_name,
        registration_date
        FROM readers
        WHERE card_number =
            (SELECT reader_card_number
             FROM log
             WHERE book_copy_inv_number = %s
             AND returning_date IS NULL);
    '''
    cursor.execute(query, (inv_number, ))
    return cursor.fetchall()


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
    return cursor.fetchall()


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
        WITH numbers AS 
            (SELECT book_copy_inv_number AS num
             FROM log where taking_date BETWEEN '%(year)s-%(month)s-01' AND LAST_DAY('%(year)s-%(month)s-01')),
             ciphers AS
            (SELECT cipher, count(*) as count
             FROM book_copies, numbers
             WHERE inv_number = numbers.num
             GROUP BY cipher)
        SELECT b.cipher, b.title, b.author, ciphers.count
        FROM books b, ciphers
        WHERE b.cipher = ciphers.cipher;
    '''
    cursor.execute(query, {'year': year, 'month': month})
    return cursor.fetchall()


def inactive_readers_for_month(cursor, year, month):
    query = '''
        SELECT card_number,
        CONCAT(surname, ' ', SUBSTRING(name, 1, 1), '.'),
        phone_number,
        room_name
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
    return cursor.fetchall()


def get_current_year_and_month(cursor):
    query = '''
        SELECT YEAR(CURDATE()), MONTH(CURDATE());
    '''
    cursor.execute(query)
    return cursor.fetchone()


def filtered_readers_search(cursor, card_number, name, surname, phone_number, room_name):
    if card_number == '':
        card_number = '%'
    name = '%' + name + '%'
    surname = '%' + surname + '%'
    if phone_number == '':
        phone_number = '%'
    if room_name == any_room_text:
        room_name = '%'
    query = '''
        SELECT card_number,
        CONCAT(surname, ' ', SUBSTRING(name, 1, 1), '.'),
        phone_number,
        room_name,
        registration_date
        FROM readers
        WHERE card_number LIKE %s
        AND name LIKE %s
        AND surname LIKE %s
        AND phone_number LIKE %s
        AND room_name LIKE %s;
    '''
    cursor.execute(query, (card_number, name, surname, phone_number, room_name))
    return cursor.fetchall()


def get_current_year(cursor):
    query = '''
        SELECT YEAR(CURDATE());
    '''
    cursor.execute(query)
    return cursor.fetchone()[0]


def get_first_year(cursor):
    query = '''
        SELECT MIN(YEAR(registration_date))
        FROM readers;
    '''
    cursor.execute(query)
    return cursor.fetchone()[0]


def cipher_exists(cursor, cipher):
    query = '''
        SELECT EXISTS 
            (SELECT cipher
             FROM books 
             WHERE cipher = %s);
    '''
    cursor.execute(query, (cipher, ))
    return cursor.fetchone()[0]


def reader_exists(cursor, card_number):
    query = '''
        SELECT EXISTS 
            (SELECT card_number
             FROM readers
             WHERE card_number = %s);
    '''
    cursor.execute(query, (card_number, ))
    return cursor.fetchone()[0]


def copy_loaned(cursor, inv_number):
    query = '''
        SELECT EXISTS
            (SELECT book_copy_inv_number
             FROM log
             WHERE book_copy_inv_number = %s
             AND returning_date IS NULL);
    '''
    cursor.execute(query, (inv_number, ))
    return cursor.fetchone()[0]


def last_copy(cursor, inv_number):
    query = '''
        SELECT 
            (SELECT count(*)
             FROM book_copies
             WHERE cipher =
                (SELECT cipher
                 FROM book_copies
                 WHERE inv_number = %s)
            ) = 1;
    '''
    cursor.execute(query, (inv_number, ))
    return cursor.fetchone()[0]


def room_not_full(cursor, room_name):
    query = '''
        SELECT capacity >
            (SELECT COUNT(*)
             FROM readers
             WHERE room_name = %s)
        FROM rooms
        WHERE name = %s;
    '''
    cursor.execute(query, (room_name, room_name))
    return cursor.fetchone()[0]


def get_timestamp(cursor):
    cursor.execute('SELECT CURRENT_TIMESTAMP();')
    return cursor.fetchone()[0]