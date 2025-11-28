import logging
import sys


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to the log level and condense the format."""

    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    blue = "\x1b[34;20m"
    reset = "\x1b[0m"

    # Condensed format: Time | Level | Name | Message
    _format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    FORMATS = {
        logging.DEBUG: grey + "DEBUG" + reset,
        logging.INFO: green + "INFO" + reset,
        logging.WARNING: yellow + "WARN" + reset,
        logging.ERROR: red + "ERROR" + reset,
        logging.CRITICAL: bold_red + "CRIT" + reset,
    }

    def format(self, record):
        # Shorten the logger name
        if record.name:
            parts = record.name.split(".")
            if len(parts) > 1:
                # Keep only the last part, or shorten the path
                # Example: sentence_transformers.SentenceTransformer -> s.SentenceTransformer
                record.name = ".".join([p[0] for p in parts[:-1]] + [parts[-1]])

            # Color the logger name
            record.name = self.blue + record.name + self.reset

        log_fmt = self._format.replace(
            "%(levelname)s", self.FORMATS.get(record.levelno, record.levelname)
        )
        # Short time format: HH:MM:SS
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)


def configure_logging(level: str = "INFO"):
    """
    Configures the root logger with a custom colored formatter.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredFormatter())

    # Get numeric level
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        handlers=[handler],
        force=True,  # Override any existing configuration
    )

    # Log the configuration change
    logging.getLogger("newsfeed.logger").info(f"Log level set to {level.upper()}")
