import asyncio
import logging

import aiohttp_jinja2
import jinja2
import aiohttp
from aiohttp import web

from tools import get_repositories_info


async def navigator_handle(request):
    """
    Base handler, take "search_term" from request and proceed repositories info matching this search_term
    """
    name = request.match_info.get('search_term')
    if name is None:
        return aiohttp.web.Response(text='Please enter criteria')
    repositories = await get_repositories_info(criteria=name, loop=request.app.loop, semaphore=request.app['semaphore'])
    logging.info("Template rendered for search_term={}".format(name))
    return aiohttp_jinja2.render_template('template.html', request, repositories)


def init_front(loop):
    """
    Init front handlers, init semaphore
    :param loop: asyncio.Event_loop
    """
    logging.info('Hayhay')
    semaphore = asyncio.Semaphore(loop=loop, value=10)
    app = aiohttp.web.Application(loop=loop)
    app['semaphore'] = semaphore

    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(searchpath='./'))
    app.router.add_get('/navigator/{search_term}', navigator_handle)
    aiohttp.web.run_app(app, loop=loop)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    main_loop = asyncio.new_event_loop()
    init_front(loop=main_loop)
