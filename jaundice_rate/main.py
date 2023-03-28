import asyncio
import pathlib

import aiofiles
import aiohttp
from pymorphy2.analyzer import MorphAnalyzer

from jaundice_rate import text_tools
from jaundice_rate.adapters import SANITIZERS


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
    article_url = 'https://inosmi.ru/economic/20190629/245384784.html'
    sanitize = SANITIZERS['inosmi_ru']

    async with aiohttp.ClientSession() as session:
        html = await fetch(session, article_url)

    sanitized_html = sanitize(html)

    article_words = text_tools.split_by_words(morph=morph, text=sanitized_html)
    charged_words = await get_charged_words_from(charged_words_directory, morph)
    rate = text_tools.calculate_jaundice_rate(
        article_words=article_words,
        charged_words=charged_words,
    )
    print(f'Рейтинг: {rate}')
    print(f'Слов в статье: {len(article_words)}')


if __name__ == '__main__':
    asyncio.run(main())
