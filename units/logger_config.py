import logging
import os
import sys
from concurrent_log_handler import ConcurrentRotatingFileHandler


def setup_logger():
    log_dir = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger("my_logger")
    logger.setLevel(logging.INFO)

    # 避免重复添加处理器
    if not logger.handlers:
        # 输出到控制台
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(console_handler)

        # 输出到文件，并启用文件轮换
        log_file_path = os.path.join(log_dir, 'daily_logs.log')
        rotating_handler = ConcurrentRotatingFileHandler(
            log_file_path, "a", maxBytes=5 * 1024 * 1024, backupCount=7, encoding='utf-8'
        )
        rotating_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(rotating_handler)

    return logger