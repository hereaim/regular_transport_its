import logging
import colorlog


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s[%(asctime)s] %(levelname)s[%(module)s]: %(message)s%(reset)s',
        datefmt='%d.%m.%Y %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    ch = logging.StreamHandler()
    ch.setFormatter(console_formatter)
    logger.addHandler(ch)

    return logger
