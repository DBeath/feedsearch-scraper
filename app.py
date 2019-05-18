from feedsearch.server import app
import logging
from scrapy.utils.log import configure_logging


if __name__ == "__main__":
    configure_logging(install_root_handler=False)

    logger = logging.getLogger("feedsearch")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    app.run("localhost", 8080)