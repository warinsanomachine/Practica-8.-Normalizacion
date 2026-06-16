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

CREATE TABLE Cast (
    cast_id INT PRIMARY KEY,
    cast_name VARCHAR(255)
);

CREATE TABLE Show_Cast (
    show_id INT,
    cast_id INT,
    PRIMARY KEY (show_id, cast_id),
    FOREIGN KEY (show_id) REFERENCES Show(show_id),
    FOREIGN KEY (cast_id) REFERENCES Cast(cast_id)
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