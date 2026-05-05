-- Run this script in pgAdmin Query Tool while connected to the default "postgres" database.
-- It recreates a clean project database.

DROP DATABASE IF EXISTS pc_salon;
CREATE DATABASE pc_salon
    WITH
    ENCODING = 'UTF8'
    TEMPLATE = template0;
