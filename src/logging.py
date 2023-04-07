import logging


def debug(msg: str) -> None:
    logging.getLogger("uvicorn").debug(msg)


def info(msg: str) -> None:
    logging.getLogger("uvicorn").info(msg)


def warn(msg: str) -> None:
    logging.getLogger("uvicorn").warn(msg)


def error(msg: str) -> None:
    logging.getLogger("uvicorn").error(msg)


# disable /health endpoint logging
class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.args is None or len(record.args) >= 3:
            return True

        if not isinstance(record.args, tuple):
            return True

        return record.args[2] != "/health"


logging.getLogger("uvicorn.access").addFilter(EndpointFilter())
