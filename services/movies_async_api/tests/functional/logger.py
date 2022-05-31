LOGGER_CONFIG = {
    "version": 1,
    "formatters": {
        "basic": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "basic",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {
        '': {
            "handlers": ["default"],
            "level": "INFO",
        }
    }
}
