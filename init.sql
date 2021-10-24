-- Create rooms (reading room) table
CREATE TABLE IF NOT EXISTS rooms (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    capacity INT NOT NULL -- Each reading room have a limit of readers
);

-- Create readers table
CREATE TABLE IF NOT EXISTS readers (
    card_number INT UNSIGNED PRIMARY KEY, -- Not bank card, but reading card
    surname VARCHAR(255) NOT NULL,
    phone_number VARCHAR(16) NOT NULL,
    room_id INT NOT NULL,
    -- Each reader is placed in one of the rooms
    CONSTRAINT fk_reader_room_id FOREIGN KEY (room_id) REFERENCES rooms (id)
);

-- Create books table
CREATE TABLE IF NOT EXISTS books (
    cipher INT UNSIGNED PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    publish_year YEAR NOT NULL,
    room_id INT NOT NULL,
    -- Each book is contained in some reading room
    CONSTRAINT fk_book_room_id FOREIGN KEY (room_id) REFERENCES rooms (id)
);

-- Create taking_log table which contains records about taking books
CREATE TABLE IF NOT EXISTS log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    reader_card_number INT UNSIGNED NOT NULL, -- who took
    book_cipher INT UNSIGNED NOT NULL, -- what took
    taking_date DATE NOT NULL, -- when took
    returning_date DATE, -- when returned
    -- References to reader and book
    CONSTRAINT fk_reader_card_number
        FOREIGN KEY (reader_card_number)
            REFERENCES readers (card_number),
    CONSTRAINT fk_book_cipher
        FOREIGN KEY (book_cipher)
            REFERENCES books (cipher)
                ON UPDATE CASCADE -- cipher can be updated
);