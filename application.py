import asyncio
import logging
from operator import itemgetter
from datetime import datetime

import aiohttp_jinja2
import jinja2
import aiohttp
from aiohttp import web

# Few constants(i'd prefer to move them to another file)
# request setups
REQUEST_TIMEOUT = 2
REQUEST_COOLDOWN = 5

# urls
SEARCH_REPOSITORIES_URL = 'https://api.github.com/search/repositories'
SEARCH_COMMITS_URL = 'https://api.github.com/search/commits'

REQEST_DEFAULT_HEADERS = {
    "Accept": "application/vnd.github.cloak-preview",
}

async def api_request(url, params, semaphore, loop=None):
    """
    Async request
    """
    while True:
        with await semaphore:
            try:
                with aiohttp.Timeout(REQUEST_TIMEOUT, loop=loop):
                    async with aiohttp.ClientSession(loop=loop) as session:
                        async with session.get(url=url,
                                               params=params,
                                               headers=REQEST_DEFAULT_HEADERS) as response:
                            response = await response.json()
                            response_items = response.get('items')
                            # github api has limit for requests per second, when i exceed them i ll got error message
                            if response_items is not None:
                                print("{}?{}".format(url, params))
                                if not len(response_items):
                                    print('==========broken============')
                                    from pprint import pprint
                                    print("{}?{}".format(url, params))
                                    pprint(response)

                                return response_items
                            print("continue parsing:{}?{}".format(url, params))
            except asyncio.TimeoutError:
                continue
        await asyncio.sleep(REQUEST_COOLDOWN, loop=loop)
    return None


def format_time(update_time):
    """
    Remove alphabetic chars from time
    :param update_time: "2017-01-27T20:43:31Z"
    :return: 2017-01-27 20:43:31
    """
    # easier variant just replace 'T' and 'Z' with spaces, but strftime better for future possible formatting
    return datetime.strftime(datetime.strptime(update_time, '%Y-%m-%dT%H:%M:%SZ'), '%Y-%m-%d %H:%M:%S')


def get_commit_info(commits):
    """
    :param commits[{
        "url": "https://api.github.com/repos/octocat/Spoon-Knife/commits/d0dd1f61b33d64e29d8bc1372a94ef6a2fee76a9",
        "sha": "d0dd1f61b33d64e29d8bc1372a94ef6a2fee76a9",
        "commit": {
            "committer": {
                "date": "2014-02-12T15:20:44-08:00",
                "name": "The Octocat",
                "email": "octocat@nowhere.com"
            },
            "message": "Pointing to the guide for forking",
        },
        "parents": [
            {
                "url": "https://api.github.com/repos/octocat/Spoon-Knife/commits/bb4cc8d3b2e14b3af5df699876dd4ff3acd00",
                "html_url": "https://github.com/octocat/Spoon-Knife/commit/bb4cc8d3b2e14b3af5df699876dd4ff3acd00b7f",
                "sha": "bb4cc8d3b2e14b3af5df699876dd4ff3acd00b7f"
            }
        ]},
    ...  # few commits possible, ordered by commit time(desc)
    ]
    :return: {
        'sha': "d0dd1f61b33d64e29d8bc1372a94ef6a2fee76a9",
        'commit_message': "Pointing to the guide for forking",
        'commit_author_name': "The Octocat"
    }
    """
    if not commits:
        return {'sha': 'repository is empty'}
    return {
        'commit_message': commits[0]['commit']['message'],
        'commit_author_name': commits[0]['commit']['committer']['name'],
        'sha': commits[0]['sha'],
    }

async def get_last_commit_info(repository_name, semaphore, loop=None):
    """
    :param repository_name: defunkt/gibberish # like {author}/repository_name
    :return: {
        'commit_sha' : 1223,
        'commit_message': 'message of last commit',
        'commit_author_name': 'name of author',
    }
    """
    commits = await api_request(url=SEARCH_COMMITS_URL,
                                params={'q': 'repo:{} is:public'.format(repository_name),
                                        'sort': 'committer-date-desc'},
                                semaphore=semaphore,
                                loop=loop)
    return get_commit_info(commits)


async def proceed_repo_dict(repository_info, semaphore, loop=None):
    last_commit_info = await get_last_commit_info(repository_info['full_name'], semaphore, loop=loop)
    return {
        'name': repository_info['name'],
        'created_at': format_time(repository_info['created_at']),
        'owner_url': repository_info['owner']['url'],
        'avatar_url': repository_info['owner']['avatar_url'],
        'owner_login': repository_info['owner']["login"],
        **last_commit_info
    }


async def get_repositories_info(criteria, semaphore, loop=None):
    response = await api_request(url=SEARCH_REPOSITORIES_URL,
                                 params={'q': criteria},
                                 loop=loop,
                                 semaphore=semaphore)
    result_data = {
        'search_term': criteria,
        'repos': []
    }
    # coroutines parallel execution
    tasks = [proceed_repo_dict(repository_info, semaphore, loop=loop) for repository_info in response[:5]]
    for coro in asyncio.as_completed(tasks, loop=loop):
        result_data['repos'].append(await coro)
    # cause processing runs async, and i dont know which coro will be finished first, i prefer to sort items, after
    # processing finished
    result_data['repos'].sort(key=itemgetter('created_at'), reverse=True)
    return result_data

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
    semaphore = asyncio.Semaphore(loop=loop, value=10)
    app = aiohttp.web.Application(loop=loop)
    app['semaphore'] = semaphore

    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(searchpath='./'))
    app.router.add_get('/navigator/{search_term}', navigator_handle)
    aiohttp.web.run_app(app, loop=loop)

if __name__ == '__main__':
    main_loop = asyncio.new_event_loop()
    init_front(loop=main_loop)
