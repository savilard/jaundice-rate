from contextlib import contextmanager

import aiohttp

from jaundice_rate import adapters
from jaundice_rate.process_articles import Article
from jaundice_rate.process_articles import ProcessingStatus


@contextmanager
def handle_exceptions(articles_stats, url):
    """Handle exceptions.

    Args:
        articles_stats: articles stats
        url: article url
    """
    try:
        yield articles_stats, url
    except aiohttp.ClientResponseError:
        articles_stats.append(
            Article(url=url, status=ProcessingStatus.FETCH_ERROR.value),
        )
    except TimeoutError:
        articles_stats.append(
            Article(url=url, status=ProcessingStatus.TIMEOUT.value),
        )
    except adapters.ArticleNotFoundError:
        articles_stats.append(
            Article(url=url, status=ProcessingStatus.PARSING_ERROR.value),
        )
