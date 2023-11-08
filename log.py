import logging

def logger(level=logging.DEBUG):
    formatter = logging.Formatter(fmt='%(asctime)s [%(module)s] %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger
