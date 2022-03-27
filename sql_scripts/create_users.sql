-- Creating of librarians accounts

-- Creating the role 'librarian' and 'admin'
CREATE ROLE 'librarian';
CREATE ROLE 'admin_role';

-- Grant privileges to librarians
GRANT SELECT ON library.* TO 'librarian';
GRANT INSERT ON library.readers TO 'librarian';
GRANT DELETE ON library.books TO 'librarian';
GRANT UPDATE ON library.books TO 'librarian';

-- Grant privileges to admins
GRANT ALL ON library.* TO 'admin_role';

-- Create accounts
CREATE USER 'Tom Cruise'@'%' IDENTIFIED BY 'mazzerati-rockfrog';
CREATE USER 'Natali Portman'@'%' IDENTIFIED BY 'capitan-sparrow-chuachua';
CREATE USER 'Tony Stark'@'%' IDENTIFIED BY 'it-was-not-fair-bro';
CREATE USER 'admin'@'%' IDENTIFIED BY 'masterpassword';

-- Grant librarian's privileges to them
GRANT 'librarian' TO 'Tom Cruise'@'%';
GRANT 'librarian' TO 'Natali Portman'@'%';
GRANT 'librarian' TO 'Tony Stark'@'%';
-- Grant admins privileges
GRANT 'admin_role' TO 'admin'@'%';

-- Assign to active the role when connection established
SET DEFAULT ROLE 'librarian' TO
    'Natali Portman'@'%',
    'Tom Cruise'@'%',
    'Tony Stark'@'%';
SET DEFAULT ROLE 'admin_role' TO
    'admin'@'%';