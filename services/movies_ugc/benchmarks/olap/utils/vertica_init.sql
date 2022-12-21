CREATE TABLE IF NOT EXISTS views
(
    id           UUID DEFAULT UUID_GENERATE(),
    user_id      UUID    NOT NULL,
    movie_id     UUID    NOT NULL,
    viewed_frame INTEGER NOT NULL
);
