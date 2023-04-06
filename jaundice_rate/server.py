import http

from aiohttp import web
from pymorphy2.analyzer import MorphAnalyzer

from jaundice_rate.process_articles import get_charged_words_from
from jaundice_rate.process_articles import process_articles_from


async def index(request):
    """Handle index page.

    Args:
        request: aiohttp request

    Returns:
        object: aiohttp json response
    """
    param = request.query.get('urls')
    if param is None:
        return web.json_response(
            data={'error': 'Pass at least one article address via the urls parameter'},
            status=http.HTTPStatus.NOT_FOUND,
        )
    urls = param.split(',')

    if len(urls) > 10:
        return web.json_response(
            data={'error': 'Too many urls in request, should be 10 or less'},
            status=http.HTTPStatus.BAD_REQUEST,
        )

    articles_stats = await process_articles_from(
        urls=urls,
        morph=request.app['morph'],
        charged_words=request.app['charged_words'],
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

    app['morph'] = MorphAnalyzer()
    app['charged_words'] = await get_charged_words_from(
        directory='jaundice_rate/charged_dict',
        morph=app['morph'],
    )
    return app


if __name__ == '__main__':
    web.run_app(init())
