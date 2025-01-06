CREATE TABLE User (
    ID VARCHAR(20) PRIMARY KEY,
    pwd VARCHAR(20)
);

INSERT INTO User(ID, pwd) VALUES ('abc@gmail.com', 'abc123');
INSERT INTO User(ID, pwd) VALUES ('777@gmail.com', '777123');
INSERT INTO User(ID, pwd) VALUES ('qwe@gmail.com', 'qwe123');
INSERT INTO User(ID, pwd) VALUES ('555@gmail.com', '555123');

SELECT * FROM User;
