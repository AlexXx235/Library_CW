-- Create library database
CREATE DATABASE IF NOT EXISTS library;
USE library;

-- Create rooms (reading room) table
CREATE TABLE IF NOT EXISTS rooms (
    name VARCHAR(128) PRIMARY KEY,
    capacity INT UNSIGNED NOT NULL -- Each reading room have a limit of readers
);

-- Create readers table
CREATE TABLE IF NOT EXISTS readers (
    card_number INT UNSIGNED PRIMARY KEY, -- Not bank card, but reading card
    name VARCHAR(128) NOT NULL,
    surname VARCHAR(128) NOT NULL,
    phone_number VARCHAR(11) NOT NULL UNIQUE,
    room_name VARCHAR(128) NOT NULL,
    registration_date DATE NOT NULL,
    -- Each reader is placed in one of the rooms
    CONSTRAINT fk_reader_room_name FOREIGN KEY (room_name) REFERENCES rooms (name)
);

-- Create books table
CREATE TABLE IF NOT EXISTS books (
    cipher INT UNSIGNED PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    author VARCHAR(256) NOT NULL
);

-- Create book_copies table
CREATE TABLE IF NOT EXISTS book_copies (
    inv_number INT UNSIGNED PRIMARY KEY,
    cipher INT UNSIGNED NOT NULL,
    room_name VARCHAR(128) NOT NULL,
    release_year YEAR NOT NULL,

    CONSTRAINT fk_copy_cipher FOREIGN KEY (cipher) REFERENCES books (cipher) ON UPDATE CASCADE,
    CONSTRAINT fk_copy_room_name FOREIGN KEY (room_name) REFERENCES rooms (name)
);

-- Create taking_log table which contains records about taking books
CREATE TABLE IF NOT EXISTS log (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    reader_card_number INT UNSIGNED NOT NULL, -- who took
    book_copy_inv_number INT UNSIGNED NOT NULL, -- what took
    taking_date DATE NOT NULL, -- when took
    returning_date DATE, -- when returned
    -- References to reader and book
    CONSTRAINT fk_reader_card_number
        FOREIGN KEY (reader_card_number)
            REFERENCES readers (card_number),
    CONSTRAINT fk_book_cipher
        FOREIGN KEY (book_copy_inv_number)
            REFERENCES book_copies (inv_number)
);