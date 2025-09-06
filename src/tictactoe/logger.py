"""
Logger singleton class for developer experience.

This logger is designed for development and debugging purposes only.
It provides structured logging with both console and file output,
including log rotation to prevent excessive disk usage.
"""

import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


class Logger:
    """
    Singleton logger class for developer experience.

    Features:
    - Singleton pattern ensures only one logger instance
    - Console and file output with rotation
    - Configurable log levels and formats
    - Automatic log directory creation
    - Thread-safe logging
    """

    _instance: Optional["Logger"] = None
    _initialized: bool = False

    def __new__(cls) -> "Logger":
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        name: str = "tictactoe",
        log_file: str = None,
        max_bytes: int = 5 * 1024 * 1024,
        backup_count: int = 5,
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
    ) -> None:
        """
        Initialize the logger singleton.

        Args:
            name: Logger name identifier
            log_file: Path to log file (relative to project root)
            max_bytes: Maximum log file size before rotation (bytes)
            backup_count: Number of backup files to keep
            console_level: Minimum log level for console output
            file_level: Minimum log level for file output
        """
        if self._initialized:
            return

        self._initialized = True
        self._name = name

        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._log_file = f"logs/tictactoe_{timestamp}.log"
        else:
            self._log_file = log_file

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if self.logger.handlers:
            return

        log_path = Path(self._log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        self._setup_console_handler(console_level)
        self._setup_file_handler(file_level, max_bytes, backup_count)

        self.logger.info("Logger initialized successfully")

    def _setup_console_handler(self, level: int) -> None:
        """Setup console handler for immediate feedback."""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        console_formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S")
        console_handler.setFormatter(console_formatter)

        self.logger.addHandler(console_handler)

    def _setup_file_handler(self, level: int, max_bytes: int, backup_count: int) -> None:
        """Setup file handler with rotation."""
        file_handler = RotatingFileHandler(self._log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        file_handler.setLevel(level)

        file_formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(file_formatter)

        self.logger.addHandler(file_handler)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        self.logger.exception(message, **kwargs)

    def set_console_level(self, level: int) -> None:
        """Change console log level dynamically."""
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, RotatingFileHandler):
                handler.setLevel(level)
                self.info(f"Console log level changed to {logging.getLevelName(level)}")

    def set_file_level(self, level: int) -> None:
        """Change file log level dynamically."""
        for handler in self.logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                handler.setLevel(level)
                self.info(f"File log level changed to {logging.getLevelName(level)}")

    def get_log_file_path(self) -> str:
        """Get the current log file path."""
        return self._log_file

    def clear_logs(self) -> None:
        """Clear all log files (for testing purposes)."""
        try:
            log_path = Path(self._log_file)
            if log_path.exists():
                log_path.unlink()

            for i in range(1, 10):
                backup_path = Path(f"{self._log_file}.{i}")
                if backup_path.exists():
                    backup_path.unlink()
                else:
                    break

            self.info("Log files cleared successfully")
        except Exception as e:
            self.error(f"Failed to clear log files: {e}")

    def __repr__(self) -> str:
        """String representation of the logger."""
        return f"Logger(name='{self._name}', file='{self._log_file}')"


def get_logger() -> Logger:
    """
    Get the singleton logger instance.

    Returns:
        Logger: The singleton logger instance
    """
    return Logger()


if __name__ == "__main__":
    logger = get_logger()

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    try:
        raise ValueError("Test exception")
    except ValueError:
        logger.exception("Caught an exception")

    logger.set_console_level(logging.WARNING)
    logger.info("This won't show on console (file only)")
    logger.warning("This will show on console")

    print(f"Log file location: {logger.get_log_file_path()}")
