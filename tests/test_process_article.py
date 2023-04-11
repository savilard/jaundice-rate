import pytest

import jaundice_rate


@pytest.mark.asyncio
async def test_article_parsing_error(morph, charged_words):
    url = 'https://lenta.ru/economic/20190629/245384784.html'

    article_stats = await jaundice_rate.process_articles_from(
        morph=morph,
        urls=[url],
        charged_words=charged_words,
    )

    assert article_stats == [
        jaundice_rate.Article(
            url=url,
            status='PARSING_ERROR',
            rate=None,
            word_count=None,
        )
    ]


@pytest.mark.asyncio
async def test_article_not_found_error(morph, charged_words):
    url = 'https://inosmi.ru/economic/520190625/245384784.html'

    article_stats = await jaundice_rate.process_articles_from(
        morph=morph,
        urls=[url],
        charged_words=charged_words,
    )

    assert article_stats == [
        jaundice_rate.Article(
            url=url,
            status='FETCH_ERROR',
            rate=None,
            word_count=None,
        )
    ]


@pytest.mark.asyncio
async def test_article_fetch_timeout_error(morph, charged_words):
    url = 'https://inosmi.ru/economic/20190625/245384784.html'

    article_stats = await jaundice_rate.process_articles_from(
        morph=morph,
        urls=[url],
        charged_words=charged_words,
        fetch_timeout=0.2,
    )

    assert article_stats == [
        jaundice_rate.Article(
            url=url,
            status='TIMEOUT',
            rate=None,
            word_count=None,
        )
    ]
