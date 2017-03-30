import asyncio

import aiohttp
from aiohttp import web
import aiohttp_jinja2

import settings

async def api_request(url, search_criteria, semaphore, loop=None):
    """
    Async request
    """
    for _ in range(settings.REQUEST_MAX_RETRIES):
        try:
            with await semaphore:
                with aiohttp.Timeout(settings.REQUEST_TIMEOUT, loop=loop):
                    async with aiohttp.ClientSession(loop=loop) as session:
                        if url == settings.SEARCH_COMMITS_URL:
                            url = "{}?q={}&sort=feature sort:committer-date-desc".format(url, search_criteria)
                        else:
                            url = "{}?q={}".format(url, search_criteria)
                        # url1 = "{}?q={}&sort=feature sort:committer-date-desc".format(url, search_criteria)
                        # print(url1)
                        async with session.get(url=url,
                                               # params={'q': search_criteria},
                                               headers=settings.REQEST_DEFAULT_HEADERS) as response:
                            response = await response.json()
                            items = response.get('items')
                            if items is not None:
                                return items
                            print('Wrong keys:{} are: {}'.format(search_criteria, response.keys()))
                            await asyncio.sleep(settings.REQUEST_COOLDOWN, loop=loop)

        except asyncio.TimeoutError:
            continue
    return None


def format_time(update_time):
    pass


async def get_last_commit_info(repository_name, semaphore, loop=None):
    """
    :param repository_name: defunkt/gibberish # like {author}/repository_name
    :return: {
        'commit_sha' : 1223,
        'commit_message': 'message of last commit',
        'commit_author_name': 'name of author',
    }
    """
    response = await api_request(url=settings.SEARCH_COMMITS_URL,
                                 search_criteria='repo:{}+is:public'.format(repository_name),
                                 semaphore=semaphore,
                                 loop=loop)
    try:
        latest_commit = response[0]
    except:
        print('!!!!!!!!!!!!!!!!{}!!!!!!!!'.format(repository_name))
        from pprint import pprint
        pprint(response)
        print()
        print()
        print()
        return dict()
    # from pprint import pprint
    # pprint(latest_commit)
    return {'sha': latest_commit['sha'],
            'commit_message': latest_commit['commit']['message'],
            'commit_author_name': latest_commit['commit']['committer']['name']}


async def proceed_repo_dict(repository_info, semaphore, loop=None):
    last_commit_info = await get_last_commit_info(repository_info['full_name'], semaphore, loop=loop)
    return {
        'name': repository_info['name'],
        'created_at': repository_info['created_at'].replace('T', ' ').replace('Z', ' '),
        'owner_url': repository_info['owner']['url'],
        'avatar_url': repository_info['owner']['avatar_url'],
        'owner_login': repository_info['owner']["login"],
        **last_commit_info
    }


async def get_repos(criteria, semaphore, loop=None):
    response = await api_request(url=settings.SEARCH_REPOSITORIES_URL,
                                 search_criteria=criteria,
                                 loop=loop,
                                 semaphore=semaphore)
    # from pprint import pprint
    # pprint(response)
    result_data = {
        'search_term': criteria,
        'repos': []
    }
    tasks = [proceed_repo_dict(repository_info, semaphore, loop=loop) for repository_info in response]
    for coro in asyncio.as_completed(tasks, loop=loop):
        # res = await coro
        # from pprint import pprint
        # pprint(res)
        result_data['repos'].append(await coro)
    return result_data

# @aiohttp_jinja2.template('template.html')
async def navigator_handle(request):
    name = request.match_info.get('search_term')
    if name is None:
        return aiohttp.web.Response(text='Please enter criteria')
    resp = await get_repos(criteria=name, loop=request.app.loop, semaphore=request.app['semaphore'])
    text = "Hello, Dude, U searched for '{}'".format(name)
    import logging
    logging.critical(text)
    # from pprint import pprint
    # pprint(resp)
    # return aiohttp.web.Response(text=resp)
    # return aiohttp.web.json_response(resp)
    return aiohttp_jinja2.render_template('template.html', request, resp)
    # return resp


def init_front(loop):
    semaphore = asyncio.Semaphore(loop=loop, value=3)
    app = aiohttp.web.Application(loop=loop)
    app['semaphore'] = semaphore
    import aiohttp_jinja2
    import jinja2

    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(searchpath='./'))
    app.router.add_get('/navigator/{search_term}', navigator_handle)
    aiohttp.web.run_app(app, loop=loop)
