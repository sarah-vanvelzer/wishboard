ALTER TABLE pins ADD COLUMN cluster INT;

CREATE TABLE themes (
    id SERIAL PRIMARY KEY,
    cluster INT NOT NULL,
    name TEXT NOT NULL,
    giftability INT NOT NULL,
    reason TEXT NOT NULL DEFAULT '',
    size INT NOT NULL,
    score REAL NOT NULL
);