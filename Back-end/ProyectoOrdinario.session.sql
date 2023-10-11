CREATE DATABASE ordinario;

--@block
USE ordinario;

--@block
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    correo VARCHAR(100),
    username VARCHAR(30) NOT NULL,
    name VARCHAR(30) NOT NULL,
    apellido_paterno VARCHAR(30),
    apellido_materno VARCHAR(30),
    password VARCHAR(30) NOT NULL,
    telefono VARCHAR(15),
    cumpleanos DATE
);

--@block
CREATE TABLE imagenes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255),
    imagen LONGBLOB
);

--@block
CREATE TABLE articles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    content VARCHAR(3000) NOT NULL
);

--@block
CREATE TABLE iconos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255),
    imagen LONGBLOB
);

--@block
DESCRIBE users;

--@block
DESCRIBE imagenes;

--@block
DESCRIBE articles;

--@block
SELECT * FROM users;

--@block
SELECT * FROM iconos;

--@block
SELECT * FROM articles;

--@block
DROP TABLE users;

--@block
Drop table articles;

--@block
Drop table iconos;

--@block
Drop DATABASE ordinario;
