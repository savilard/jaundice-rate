import http

from aiohttp import web
from pymorphy2.analyzer import MorphAnalyzer

import jaundice_rate


async def index(request):
    """Handle index page.

    Args:
        request: aiohttp request

    Returns:
        object: aiohttp json response
    """
    settings = request.app['settings']
    morph = request.app['morph']

    parameter_with_urls = request.query.get('urls')
    if parameter_with_urls is None:
        return web.json_response(
            data={
                'error': 'Pass at least one article address via the urls parameter',
            },
            status=http.HTTPStatus.NOT_FOUND,
        )

    urls = parameter_with_urls.split(',')
    if len(urls) > settings.url_limit:
        return web.json_response(
            data={'error': 'Too many urls in request, should be 10 or less'},
            status=http.HTTPStatus.BAD_REQUEST,
        )

    charged_words = await jaundice_rate.get_charged_words_from(
        path_to_directory=settings.charged_words_directory,
        morph=morph,
    )

    articles_stats = await jaundice_rate.process_articles_from(
        urls=urls,
        morph=morph,
        charged_words=charged_words,
        fetch_timeout=settings.fetch_timeout,
    )
    payload = {
        'status': 'OK',
        'data': [article_stats.to_dict() for article_stats in articles_stats],
    }
    return web.json_response(data=payload, status=http.HTTPStatus.OK)


async def init():
    """Init aiohttp server app.

    Returns:
        object: aiohttp app
    """
    app = web.Application()
    app.add_routes([web.get('/', index)])

    app['settings'] = jaundice_rate.Settings()
    app['morph'] = MorphAnalyzer()

    return app


if __name__ == '__main__':
    web.run_app(init())
