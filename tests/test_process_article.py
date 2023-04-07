import pytest

from jaundice_rate.process_articles import Article
from jaundice_rate.process_articles import process_articles_from


@pytest.mark.asyncio
async def test_article_parsing_error(morph):
    url = 'https://lenta.ru/economic/20190629/245384784.html'
    charged_words = ['во-первых', 'хотеть', 'чтобы']

    article_stats = await process_articles_from(
        morph=morph,
        urls=[url],
        charged_words=charged_words,
    )

    assert article_stats == [Article(url=url, status='PARSING_ERROR', rate=None, word_count=None, elapsed_time=None)]
