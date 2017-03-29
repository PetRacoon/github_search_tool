import asyncio

import aiohttp
from aiohttp import web

import settings

async def search_repos(search_criteria, loop=None):
    """
    Async request
    """
    for _ in range(settings.REQUEST_MAX_RETRIES):
        try:
            with aiohttp.Timeout(settings.REQUEST_TIMEOUT, loop=loop):
                async with aiohttp.ClientSession(loop=loop) as session:
                    async with session.get(url=settings.BASE_SEARCH_URL,
                                           params={'q': search_criteria}) as response:
                            return await response.json()
        except asyncio.TimeoutError:
            await asyncio.sleep(settings.REQUEST_COOLDOWN, loop=loop)
    return None

async def navigator_handle(request):
    name = request.match_info.get('search_term')
    if name is None:
        return aiohttp.web.Response(text='Please enter criteria')
    resp = await search_repos(search_criteria=name, loop=request.app.loop)
    text = "Hello, Dude, U searched for '{}'".format(name)
    import logging
    logging.critical(text)
    # return aiohttp.web.Response(text=resp)
    return aiohttp.web.json_response(resp)

def init_front(loop):
    app = aiohttp.web.Application(loop=loop)
    app.router.add_get('/navigator/{search_term}', navigator_handle)
    aiohttp.web.run_app(app, loop=loop)
