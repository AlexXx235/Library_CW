-- Creating of librarians accounts

-- Creating the role 'librarian'
CREATE ROLE 'librarian';
-- Grant privileges to librarians
GRANT SELECT ON library.* TO 'librarian';
GRANT INSERT ON library.readers TO 'librarian';
GRANT DELETE ON library.books TO 'librarian';
GRANT UPDATE ON library.books TO 'librarian';
-- Create accounts
CREATE USER 'Tom Cruise'@'%' IDENTIFIED BY 'mazzerati-rockfrog';
CREATE USER 'Natali Portman'@'%' IDENTIFIED BY 'capitan-sparrow-chuachua';
CREATE USER 'Tony Stark'@'%' IDENTIFIED BY 'it-was-not-fair-bro';
-- Grant librarian's privileges to them
GRANT 'librarian' TO 'Tom Cruise'@'%';
GRANT 'librarian' TO 'Natali Portman'@'%';
GRANT 'librarian' TO 'Tony Stark'@'%';
-- Assign to active the role when connection established
SET DEFAULT ROLE 'librarian' TO
    "Natali Portman",
    "Tom Cruise",
    "Tony Stark";