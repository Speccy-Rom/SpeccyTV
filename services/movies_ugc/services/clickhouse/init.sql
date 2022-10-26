CREATE TABLE default.user_events (
    id           UUID DEFAULT generateUUIDv4(),
    user_id      UUID,
    movie_id     UUID,
    event        String,
    frame        Int32,
    event_time   DateTime('Europe/Moscow')
) ENGINE = MergeTree() ORDER BY id;


CREATE TABLE default.users_login (
    id           UUID DEFAULT generateUUIDv4(),
    user_id      UUID,
    user_ip      String,
    user_agent   String,
    login_time   DateTime('Europe/Moscow')
) ENGINE = MergeTree() ORDER BY id;
