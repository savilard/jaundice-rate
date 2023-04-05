from contextlib import contextmanager
import enum
import pathlib
import time
from typing import NamedTuple
import urllib

import aiofiles
import aiohttp
import anyio
import pymorphy2

from jaundice_rate import adapters
from jaundice_rate import text_tools

FETCH_TIMEOUT = 3


class ProcessingStatus(enum.Enum):
    """The status of the processing of the article on the above link."""

    OK = 'OK'
    FETCH_ERROR = 'FETCH_ERROR'
    PARSING_ERROR = 'PARSING_ERROR'
    TIMEOUT = 'TIMEOUT'


class ArticleStats(NamedTuple):
    """Article stats attributes."""

    url: str
    status: str
    rate: float | None = None
    word_count: int | None = None
    elapsed_time: float | None = None

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
            'elapsed_time': self.elapsed_time,
        }


@contextmanager
def timeit():
    """Measures the time of the function."""
    start = time.monotonic()

    class _Timer:  # noqa: WPS431
        duration = time.monotonic() - start

    yield _Timer

    _Timer.duration = time.monotonic() - start


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
            ArticleStats(url=url, status=ProcessingStatus.FETCH_ERROR.value),
        )
    except TimeoutError:
        articles_stats.append(
            ArticleStats(url=url, status=ProcessingStatus.TIMEOUT.value),
        )
    except adapters.ArticleNotFound:
        articles_stats.append(
            ArticleStats(url=url, status=ProcessingStatus.PARSING_ERROR.value),
        )


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    """Fetch an article from her url.

    Args:
        session: aiohttp client session
        url: article url

    Returns:
        object: article text
    """
    async with anyio.fail_after(delay=FETCH_TIMEOUT):
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()


def get_sanitizer_for(url: str):
    """Get sanitizer for url domain.

    Args:
        url: article url

    Returns:
        object: article sanitizer

    Raises:
        ArticleNotFound: no sanitizer found for the article
    """
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc
    try:
        return adapters.SANITIZERS[domain]
    except KeyError:
        raise adapters.ArticleNotFound()


async def process_article(
    session: aiohttp.ClientSession,
    morph: pymorphy2.MorphAnalyzer,
    charged_words: list[str],
    url: str,
    article_statistics,
) -> ArticleStats:
    """Calculate article statistics.

    Args:
        session: aiohttp ClientSession
        morph: pymorphy2 morph analyzer
        charged_words: charged words
        url: article url
        article_statistics:article statistics
    """
    with handle_exceptions(articles_stats=article_statistics, url=url):
        html = await fetch(session=session, url=url)
        sanitize = get_sanitizer_for(url)

        with timeit() as elapsed_time:
            article_words = await text_tools.split_by_words(
                morph=morph,
                text=sanitize(html),
            )

        rate = text_tools.calculate_jaundice_rate(
            article_words=article_words,
            charged_words=charged_words,
        )
        article_statistics.append(
            ArticleStats(
                url=url,
                status=ProcessingStatus.OK.value,
                rate=rate,
                word_count=len(article_words),
                elapsed_time=round(elapsed_time.duration, 2),  # noqa: WPS441
            ),
        )


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
    directory: str,
    morph: pymorphy2.MorphAnalyzer,
) -> list[str]:
    """Get the list of charged words from the files in the specified directory.

    Args:
        directory: path to directory with files
        morph: MorphAnalyzer

    Returns:
        object: list of charged words
    """
    return [
        await text_tools.split_by_words(
            morph=morph,
            text=await extract_file_content_from(filepath),
        )
        for filepath in pathlib.Path(directory).glob('**/*.txt')
    ][0]


async def process_articles_from(
    urls: list[str],
    morph: pymorphy2.MorphAnalyzer,
    charged_words: list[str],
):
    """Start processing articles.

    Args:
        urls: articles urls
        morph: pymorphy2 MorphAnalyzer
        charged_words: charged words

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
                )

    return articles_stats


async def main():
    """Entry point."""
    morph = pymorphy2.MorphAnalyzer()
    charged_words_directory = 'jaundice_rate/charged_dict'
    charged_words = await get_charged_words_from(charged_words_directory, morph)

    urls = [
        'https://inosmi.ru/20230328/indiya-261728000.html',
        'https://inosmi.ru/20230328/kosovo-261727700.html',
    ]

    await process_articles_from(
        urls=urls,
        morph=morph,
        charged_words=charged_words,
    )


if __name__ == '__main__':
    anyio.run(main)
