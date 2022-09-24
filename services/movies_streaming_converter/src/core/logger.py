LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DEFAULT_HANDLERS = [
    "console",
]


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": LOG_FORMAT},
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "logstash": {
            "level": "DEBUG",
            "filters": ["request-id"],
            "class": "logstash.LogstashHandler",
            "host": "logstash",
            "port": 5045,
            "version": 1,
            "message_type": "logstash",
            "fqdn": False,
            "tags": ["tag1", "tag2"],
        },
    },
    "loggers": {
        "": {
            "handlers": LOG_DEFAULT_HANDLERS,
            "level": "DEBUG",
        },
        "uvicorn.error": {
            "level": "INFO",
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
        "fastapi.request": {
            "handlers": ["logstash"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
    "root": {
        "level": "INFO",
        "formatter": "verbose",
        "handlers": LOG_DEFAULT_HANDLERS,
    },
}
