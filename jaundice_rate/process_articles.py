from contextlib import contextmanager
import enum
import logging
import pathlib
import time
from typing import NamedTuple
import urllib

import aiofiles
import aiohttp
import anyio
import pymorphy2

import jaundice_rate

logger = logging.getLogger('articles_stats')


class ProcessingStatus(enum.Enum):
    """The status of the processing of the article on the above link."""

    OK = 'OK'
    FETCH_ERROR = 'FETCH_ERROR'
    PARSING_ERROR = 'PARSING_ERROR'
    TIMEOUT = 'TIMEOUT'


class Article(NamedTuple):
    """Article attributes."""

    url: str
    status: str
    rate: float | None = None
    word_count: int | None = None

    def to_dict(self):
        """Convert article stats to dict.

        Returns:
            object: article stats dict
        """
        return {
            'url': self.url,
            'status': self.status,
            'rate': self.rate,
            'word_count': self.word_count,
        }


@contextmanager
def timeit():
    """Measures the time of the function."""
    start_time = time.monotonic()
    yield
    elapsed_time = time.monotonic() - start_time
    logging.info(f'The analysis is complete for {round(elapsed_time, 2)} sec.')


async def fetch(
    session: aiohttp.ClientSession,
    url: str,
    timeout: int | float = 3,
) -> str:
    """Fetch an article from her url.

    Args:
        session: aiohttp client session
        url: article url
        timeout: article fetch timeout in seconds

    Returns:
        object: article text
    """
    async with anyio.fail_after(delay=timeout):
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()


def get_adapter_for(url: str):
    """Get adapter for url domain.

    Args:
        url: article url

    Returns:
        object: article sanitizer

    Raises:
        ArticleNotFoundError: no adapter found for the article
    """
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc
    try:
        return jaundice_rate.SANITIZERS[domain]
    except KeyError:
        raise jaundice_rate.ArticleNotFoundError()


async def extract_file_content_from(filepath: pathlib.Path) -> str:
    """Extract file content from file.

    Args:
        filepath: the path to the file with the necessary information

    Returns:
        object: file content
    """
    async with aiofiles.open(filepath, mode='r') as fd:
        return await fd.read()


async def get_charged_words_from(
    path_to_directory: str,
    morph: pymorphy2.MorphAnalyzer,
) -> list[str]:
    """Get the list of charged words from the files in the specified directory.

    Args:
        path_to_directory: path to directory with files
        morph: MorphAnalyzer

    Returns:
        object: list of charged words
    """
    return [
        await jaundice_rate.split_by_words(
            morph=morph,
            text=await extract_file_content_from(filepath),
        )
        for filepath in pathlib.Path(path_to_directory).glob('**/*.txt')
    ][0]


async def process_article(
    session: aiohttp.ClientSession,
    morph: pymorphy2.MorphAnalyzer,
    charged_words: list[str],
    url: str,
    article_stats: list[Article],
    fetch_timeout: int | float = 3,
) -> None:
    """Calculate article statistics.

    Args:
        session: aiohttp ClientSession
        morph: pymorphy2 morph analyzer
        charged_words: charged words
        url: article url
        article_stats:article statistics
        fetch_timeout: article fetch timeout in seconds
    """
    with jaundice_rate.handle_exceptions(articles_stats=article_stats, url=url):
        sanitize = get_adapter_for(url)
        html = await fetch(session=session, url=url, timeout=fetch_timeout)

        with timeit():
            article_words = await jaundice_rate.split_by_words(
                morph=morph,
                text=sanitize(html),
            )

        rate = jaundice_rate.calculate_jaundice_rate(
            article_words=article_words,
            charged_words=charged_words,
        )
        article_stats.append(
            Article(
                url=url,
                status=ProcessingStatus.OK.value,
                rate=rate,
                word_count=len(article_words),
            ),
        )


async def process_articles_from(
    urls: list[str],
    morph: pymorphy2.MorphAnalyzer,
    charged_words: list[str],
    fetch_timeout: int | float = 3,
):
    """Start processing articles.

    Args:
        urls: articles urls
        morph: pymorphy2 MorphAnalyzer
        charged_words: charged words
        fetch_timeout: article fetch timeout in seconds

    Returns:
        objects: articles_stats
    """
    articles_stats = []

    async with aiohttp.ClientSession() as session:
        async with anyio.create_task_group() as tg:
            for url in urls:
                tg.start_soon(
                    process_article,
                    session,
                    morph,
                    charged_words,
                    url,
                    articles_stats,
                    fetch_timeout,
                )

    return articles_stats
