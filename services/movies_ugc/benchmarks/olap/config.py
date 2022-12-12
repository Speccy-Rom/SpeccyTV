CLICKHOUSE_HOST = 'localhost'

VERTICA_CONNECTION_PARAMS = {
    'host': '127.0.0.1',
    'port': 5433,
    'user': 'dbadmin',
    'password': '',
    'database': 'docker',
    'autocommit': True,
}

UPLOAD_BATCH_SIZE = 10_000
NUMBER_OF_BATCHES = 1000
BENCHMARK_ITERATIONS = 10
