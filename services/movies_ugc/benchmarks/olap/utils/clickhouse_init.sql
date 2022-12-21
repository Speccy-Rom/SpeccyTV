CREATE TABLE IF NOT EXISTS views
(
    id           UUID DEFAULT generateUUIDv4(),
    user_id      UUID NOT NULL,
    movie_id     UUID NOT NULL,
    viewed_frame INTEGER NOT NULL
)
    ENGINE = MergeTree() ORDER BY id;
