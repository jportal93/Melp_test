CREATE TABLE Restaurants (
    id TEXT PRIMARY KEY,
    rating INTEGER,
    name TEXT,
    site TEXT,
    email TEXT,
    phone TEXT,
    street TEXT,
    city TEXT,
    state TEXT,
    lat FLOAT,
    lng FLOAT
);

COPY Restaurants FROM '/srv/restaurantes.csv' DELIMITER ',' CSV HEADER;
