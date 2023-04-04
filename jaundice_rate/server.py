from aiohttp import web


async def handle(request):
    urls = request.query.get('urls', 'None')
    payload = {
        'urls': urls.split(','),
    }
    return web.json_response(data=payload)


app = web.Application()
app.add_routes([web.get('/', handle)])

if __name__ == '__main__':
    web.run_app(app)
