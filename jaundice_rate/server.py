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
    urls = request.query.get('urls')
    if urls is None:
        return web.json_response(
            data={'error': 'Pass at least one article address via the urls parameter'},
            status=http.HTTPStatus.BAD_REQUEST,
        )
    article_statistics = await process_articles_from(
        urls=urls.split(','),
        morph=request.app['morph'],
        charged_words=request.app['charged_words'],
    )
    return web.json_response(data=article_statistics)


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
