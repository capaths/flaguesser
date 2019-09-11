CREATE DATABASE ticket;
\c ticket

CREATE TABLE tickets (id bigserial primary key, title VARCHAR (50), description VARCHAR (355));

INSERT INTO tickets(title,description) VALUES ('test 1','test description 1');
INSERT INTO tickets(title,description) VALUES ('test 2','test description 2');
INSERT INTO tickets(title,description) VALUES ('test 3','test description 3');
INSERT INTO tickets(title,description) VALUES ('test 4','test description 4');