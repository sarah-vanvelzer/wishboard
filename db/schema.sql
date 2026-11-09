CREATE TABLE pins (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    board TEXT NOT NULL DEFAULT '',
    board_id TEXT NOT NULL DEFAULT '',
    image_url TEXT,
    link TEXT,
    UNIQUE (source, source_id)
);