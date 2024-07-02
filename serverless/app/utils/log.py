import os
import sys
import logging


def init_logger(module_name='default'):
    logger = logging.getLogger(module_name)
    LOG_LEVEL = get_log_level_by_env()
    logger.setLevel(LOG_LEVEL)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        stream_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    return logger


def get_log_level_by_env(is_return_name=False):
    env_log_level = os.environ.get('LOG_LEVEL')
    env = os.environ.get('FLASK_ENV')
    if env_log_level:
        log_level = env_log_level.upper()
    elif env:
        log_level = 'INFO' if env == 'production' else 'DEBUG'
    else:
        log_level = 'INFO'
    if is_return_name:
        return log_level
    return getattr(logging, log_level, logging.INFO)


def get_current_log_level(log_name=None):
    if log_name is None:
        log_name = __name__
    current_log_level = logging.getLogger(log_name).getEffectiveLevel()
    return logging.getLevelName(current_log_level)
