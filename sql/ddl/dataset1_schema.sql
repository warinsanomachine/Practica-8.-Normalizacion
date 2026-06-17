DROP TABLE IF EXISTS Show CASCADE;

DROP TABLE IF EXISTS Director CASCADE;

DROP TABLE IF EXISTS Show_Director CASCADE;

DROP TABLE IF EXISTS Actor CASCADE;

DROP TABLE IF EXISTS Show_Actor CASCADE;

DROP TABLE IF EXISTS Country CASCADE;

DROP TABLE IF EXISTS Show_Country CASCADE;

DROP TABLE IF EXISTS Listed_in CASCADE;

DROP TABLE IF EXISTS Show_Listed_in CASCADE;

CREATE TABLE Show (
    show_id INT PRIMARY KEY,
    type VARCHAR(20),
    title VARCHAR(255),
    date_added VARCHAR(50),
    release_year INT,
    rating VARCHAR(20),
    duration VARCHAR(20)
);

CREATE TABLE Director (
    director_id INT PRIMARY KEY,
    director_name VARCHAR(255)
);

CREATE TABLE Show_Director (
    show_id INT,
    director_id INT,
    PRIMARY KEY (show_id, director_id),
    FOREIGN KEY (show_id) REFERENCES Show(show_id),
    FOREIGN KEY (director_id) REFERENCES Director(director_id)
);

CREATE TABLE Actor (
    actor_id INT PRIMARY KEY,
    actor_name VARCHAR(255)
);

CREATE TABLE Show_Actor (
    show_id INT,
    actor_id INT,
    PRIMARY KEY (show_id, actor_id),
    FOREIGN KEY (show_id) REFERENCES Show(show_id),
    FOREIGN KEY (actor_id) REFERENCES Actor(actor_id)
);

CREATE TABLE Country (
    country_id INT PRIMARY KEY,
    country_name VARCHAR(255)
);

CREATE TABLE Show_Country (
    show_id INT,
    country_id INT,
    PRIMARY KEY (show_id, country_id),
    FOREIGN KEY (show_id) REFERENCES Show(show_id),
    FOREIGN KEY (country_id) REFERENCES Country(country_id)
);

CREATE TABLE Listed_in (
    listed_in_id INT PRIMARY KEY,
    listed_in_name VARCHAR(255)
);

CREATE TABLE Show_Listed_in (
    show_id INT,
    listed_in_id INT,
    PRIMARY KEY (show_id, listed_in_id),
    FOREIGN KEY (show_id) REFERENCES Show(show_id),
    FOREIGN KEY (listed_in_id) REFERENCES Listed_in(listed_in_id)
);