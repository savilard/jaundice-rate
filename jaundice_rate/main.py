import asyncio
import pathlib

import aiofiles
import aiohttp
from anyio import create_task_group
from pymorphy2.analyzer import MorphAnalyzer

from jaundice_rate import text_tools
from jaundice_rate.adapters import SANITIZERS

TEST_ARTICLES = [
    'https://inosmi.ru/20230328/indiya-261728000.html',
    'https://inosmi.ru/20230328/kosovo-261727700.html',
    'https://inosmi.ru/20230328/finlyandiya-261723675.html',
    'https://inosmi.ru/20230328/zapad-261719994.html',
    'https://inosmi.ru/20230328/ekonomika-261701001.html',
]


async def process_article(session, morph, charged_words, url, article_statistics):
    sanitize = SANITIZERS['inosmi_ru']
    html = await fetch(session=session, url=url)
    sanitized_html = sanitize(html)
    article_words = text_tools.split_by_words(
        morph=morph,
        text=sanitized_html,
    )
    score = text_tools.calculate_jaundice_rate(
        article_words=article_words,
        charged_words=charged_words,
    )

    article_statistics.append(
        {
            'url': url,
            'score': score,
            'word_count': len(article_words),
        }
    )


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def extract_file_content_from(filepath: pathlib.Path):
    async with aiofiles.open(filepath, mode='r') as fd:
        return await fd.read()


async def get_charged_words_from(directory: str, morph: MorphAnalyzer) -> list[str]:
    return [
        text_tools.split_by_words(morph=morph, text=await extract_file_content_from(filepath))
        for filepath in pathlib.Path(directory).glob('**/*.txt')
    ][0]


async def main():
    morph = MorphAnalyzer()
    charged_words_directory = 'jaundice_rate/charged_dict'
    charged_words = await get_charged_words_from(charged_words_directory, morph)
    article_statistics = []

    async with aiohttp.ClientSession() as session:
        async with create_task_group() as tg:
            for article in TEST_ARTICLES:
                tg.start_soon(process_article, session, morph, charged_words, article, article_statistics)

    for article_statistic in article_statistics:
        print('URL:', article_statistic.get('url'), 'неизвестно')
        print('Рейтинг:', article_statistic.get('score'), 'неизвестно')
        print('Слов в статье:', article_statistic.get('word_count'), 'неизвестно')
        print('-' * 10)


if __name__ == '__main__':
    asyncio.run(main())
