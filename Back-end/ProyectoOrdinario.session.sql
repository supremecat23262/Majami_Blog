CREATE DATABASE ordinario;
--@block
DROP DATABASE ordinario;
--@block
USE ordinario;

--@block
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    correo VARCHAR(30),
    username VARCHAR(15) NOT NULL,
    name VARCHAR(20) NOT NULL,
    apellido_paterno VARCHAR(20),
    apellido_materno VARCHAR(20),
    password VARCHAR(15) NOT NULL,
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
    title VARCHAR(40) NOT NULL,
    content VARCHAR(100) NOT NULL
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
Drop table articulo;

--@block
Drop table iconos;

--@block
Drop DATABASE ordinario;
--@block
SHOW VARIABLES LIKE 'have_ssl';
SHOW VARIABLES LIKE 'ssl_version';
SHOW VARIABLES LIKE 'require_secure_transport';
