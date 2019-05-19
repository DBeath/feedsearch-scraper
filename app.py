from feedsearch.server import app
import logging
from scrapy.utils.log import configure_logging


if __name__ == "__main__":
    configure_logging(install_root_handler=False)

    logger = logging.getLogger("feedsearch")
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    app.run("localhost", 8080)