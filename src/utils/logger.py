"""Logging padronizado da aplicação."""

import logging


def get_logger(name: str = "top_training") -> logging.Logger:
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)
