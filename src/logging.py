import logging


def debug(msg: str) -> None:
    logging.getLogger("uvicorn").debug(msg)


def info(msg: str) -> None:
    logging.getLogger("uvicorn").info(msg)


def warn(msg: str) -> None:
    logging.getLogger("uvicorn").warn(msg)


def error(msg: str) -> None:
    logging.getLogger("uvicorn").error(msg)
