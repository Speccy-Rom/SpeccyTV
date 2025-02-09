import logging

import config
from elastic import ElasticsearchLoader
from models import ModeETL
from pipelines import FilmWorkPipeline, GenrePipeline, PersonPipeline
from postgres import PostgresProducer
from state import JsonFileStorage, State

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('root')


def main():
    try:
        logger.info('Start ETL application with %s mode', config.ETL_MODE)

        state = State(JsonFileStorage(config.ETL_FILE_STATE))
        es_loader = ElasticsearchLoader(
            [
                'http://{host}:{port}'.format(
                    host=config.ELASTICSEARCH_HOST, port=config.ELASTICSEARCH_PORT
                )
            ]
        )
        db_adapter = PostgresProducer(
            {
                'dbname': config.POSTGRES_NAME,
                'user': config.POSTGRES_USER,
                'password': config.POSTGRES_PASSWORD,
                'host': config.POSTGRES_HOST,
                'port': config.POSTGRES_PORT,
            }
        )

        pipeline_classes = {
            ModeETL.FILM_WORK.value: FilmWorkPipeline,
            ModeETL.PERSON.value: PersonPipeline,
            ModeETL.GENRE.value: GenrePipeline,
        }

        if pipeline_class := pipeline_classes.get(config.ETL_MODE):
            pipeline = pipeline_class(state, db_adapter, es_loader)
            pipeline.etl_process()
        else:
            logger.warning(
                'Mode ETL must be from a list: %s',
                ', '.join([mode.value for mode in ModeETL]),
            )

        logger.info('End ETL application with %s mode', config.ETL_MODE)
    except Exception as e:
        logger.error('ETL process failed: %s', e)


if __name__ == '__main__':
    main()
