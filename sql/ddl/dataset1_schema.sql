
CREATE TABLE titles (
    show_id VARCHAR(50) PRIMARY KEY,
    type VARCHAR(50),
    title TEXT,
    date_added VARCHAR(100),
    release_year INT,
    rating VARCHAR(20),
    duration VARCHAR(50),
    description TEXT
);

CREATE TABLE directors (
    director_name_id INT PRIMARY KEY,
    director_name VARCHAR(255)
);

CREATE TABLE actors (
    actor_name_id INT PRIMARY KEY,
    actor_name VARCHAR(255)
);

CREATE TABLE countries (
    country_name_id INT PRIMARY KEY,
    country_name VARCHAR(100)
);

CREATE TABLE categories (
    category_name_id INT PRIMARY KEY,
    category_name VARCHAR(100)
);

-- Tablas Relacionales (Muchos a Muchos)
CREATE TABLE title_directors (
    show_id VARCHAR(50),
    director_name_id INT,
    PRIMARY KEY (show_id, director_name_id),
    FOREIGN KEY (show_id) REFERENCES titles(show_id),
    FOREIGN KEY (director_name_id) REFERENCES directors(director_name_id)
);

CREATE TABLE title_actors (
    show_id VARCHAR(50),
    actor_name_id INT,
    PRIMARY KEY (show_id, actor_name_id),
    FOREIGN KEY (show_id) REFERENCES titles(show_id),
    FOREIGN KEY (actor_name_id) REFERENCES actors(actor_name_id)
);

CREATE TABLE title_countries (
    show_id VARCHAR(50),
    country_name_id INT,
    PRIMARY KEY (show_id, country_name_id),
    FOREIGN KEY (show_id) REFERENCES titles(show_id),
    FOREIGN KEY (country_name_id) REFERENCES countries(country_name_id)
);

CREATE TABLE title_categories (
    show_id VARCHAR(50),
    category_name_id INT,
    PRIMARY KEY (show_id, category_name_id),
    FOREIGN KEY (show_id) REFERENCES titles(show_id),
    FOREIGN KEY (category_name_id) REFERENCES categories(category_name_id)
);