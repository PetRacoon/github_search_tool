import asyncio

import aiohttp
from aiohttp import web
import aiohttp_jinja2

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

def proceed_repo_dict(items):
    """
    :param items:[
    {
      "git_url": "git://github.com/TheFirePro/test.git",
      "url": "https://api.github.com/repos/TheFirePro/test",
      "tags_url": "https://api.github.com/repos/TheFirePro/test/tags",
      "full_name": "TheFirePro/test",
      "merges_url": "https://api.github.com/repos/TheFirePro/test/merges",
      "html_url": "https://github.com/TheFirePro/test",
      "archive_url": "https://api.github.com/repos/TheFirePro/test/{archive_format}{/ref}",
      "ssh_url": "git@github.com:TheFirePro/test.git",
      "svn_url": "https://github.com/TheFirePro/test",
      "contributors_url": "https://api.github.com/repos/TheFirePro/test/contributors",
      "private": false,
      "subscription_url": "https://api.github.com/repos/TheFirePro/test/subscription",
      "has_projects": true,
      "git_commits_url": "https://api.github.com/repos/TheFirePro/test/git/commits{/sha}",
      "open_issues_count": 0,
      "pulls_url": "https://api.github.com/repos/TheFirePro/test/pulls{/number}",
      "milestones_url": "https://api.github.com/repos/TheFirePro/test/milestones{/number}",
      "size": 0,
      "events_url": "https://api.github.com/repos/TheFirePro/test/events",
      "created_at": "2017-03-14T07:52:19Z",
      "assignees_url": "https://api.github.com/repos/TheFirePro/test/assignees{/user}",
      "forks_count": 0,
      "issue_events_url": "https://api.github.com/repos/TheFirePro/test/issues/events{/number}",
      "hooks_url": "https://api.github.com/repos/TheFirePro/test/hooks",
      "git_refs_url": "https://api.github.com/repos/TheFirePro/test/git/refs{/sha}",
      "owner": {
        "subscriptions_url": "https://api.github.com/users/TheFirePro/subscriptions",
        "type": "User",
        "followers_url": "https://api.github.com/users/TheFirePro/followers",
        "id": 17813861,
        "organizations_url": "https://api.github.com/users/TheFirePro/orgs",
        "gravatar_id": "",
        "events_url": "https://api.github.com/users/TheFirePro/events{/privacy}",
        "url": "https://api.github.com/users/TheFirePro",
        "gists_url": "https://api.github.com/users/TheFirePro/gists{/gist_id}",
        "login": "TheFirePro",
        "repos_url": "https://api.github.com/users/TheFirePro/repos",
        "avatar_url": "https://avatars1.githubusercontent.com/u/17813861?v=3",
        "following_url": "https://api.github.com/users/TheFirePro/following{/other_user}",
        "html_url": "https://github.com/TheFirePro",
        "site_admin": false,
        "starred_url": "https://api.github.com/users/TheFirePro/starred{/owner}{/repo}",
        "received_events_url": "https://api.github.com/users/TheFirePro/received_events"
      },
      "homepage": null,
      "notifications_url": "https://api.github.com/repos/TheFirePro/test/notifications{?since,all,participating}",
      "updated_at": "2017-03-14T07:52:19Z",
      "issue_comment_url": "https://api.github.com/repos/TheFirePro/test/issues/comments{/number}",
      "default_branch": "master",
      "subscribers_url": "https://api.github.com/repos/TheFirePro/test/subscribers",
      "git_tags_url": "https://api.github.com/repos/TheFirePro/test/git/tags{/sha}",
      "blobs_url": "https://api.github.com/repos/TheFirePro/test/git/blobs{/sha}",
      "trees_url": "https://api.github.com/repos/TheFirePro/test/git/trees{/sha}",
      "id": 84920930,
      "languages_url": "https://api.github.com/repos/TheFirePro/test/languages",
      "mirror_url": null,
      "deployments_url": "https://api.github.com/repos/TheFirePro/test/deployments",
      "score": 10.54166,
      "has_issues": true,
      "issues_url": "https://api.github.com/repos/TheFirePro/test/issues{/number}",
      "contents_url": "https://api.github.com/repos/TheFirePro/test/contents/{+path}",
      "has_downloads": true,
      "name": "test",
      "labels_url": "https://api.github.com/repos/TheFirePro/test/labels{/name}",
      "forks": 0,
      "watchers": 0,
      "clone_url": "https://github.com/TheFirePro/test.git",
      "comments_url": "https://api.github.com/repos/TheFirePro/test/comments{/number}",
      "open_issues": 0,
      "description": "Suka Blyat",
      "watchers_count": 0,
      "commits_url": "https://api.github.com/repos/TheFirePro/test/commits{/sha}",
      "stargazers_count": 0,
      "collaborators_url": "https://api.github.com/repos/TheFirePro/test/collaborators{/collaborator}",
      "keys_url": "https://api.github.com/repos/TheFirePro/test/keys{/key_id}",
      "forks_url": "https://api.github.com/repos/TheFirePro/test/forks",
      "teams_url": "https://api.github.com/repos/TheFirePro/test/teams",
      "has_wiki": true,
      "stargazers_url": "https://api.github.com/repos/TheFirePro/test/stargazers",
      "fork": false
    },
    {
      "compare_url": "https://api.github.com/repos/danira1349/suka_blyat/compare/{base}...{head}",
      "downloads_url": "https://api.github.com/repos/danira1349/suka_blyat/downloads",
      "language": null,
      "releases_url": "https://api.github.com/repos/danira1349/suka_blyat/releases{/id}",
      "statuses_url": "https://api.github.com/repos/danira1349/suka_blyat/statuses/{sha}",
      "branches_url": "https://api.github.com/repos/danira1349/suka_blyat/branches{/branch}",
      "has_pages": false,
      "pushed_at": "2017-01-27T21:21:04Z",
      "git_url": "git://github.com/danira1349/suka_blyat.git",
      "url": "https://api.github.com/repos/danira1349/suka_blyat",
      "tags_url": "https://api.github.com/repos/danira1349/suka_blyat/tags",
      "full_name": "danira1349/suka_blyat",
      "merges_url": "https://api.github.com/repos/danira1349/suka_blyat/merges",
      "html_url": "https://github.com/danira1349/suka_blyat",
      "archive_url": "https://api.github.com/repos/danira1349/suka_blyat/{archive_format}{/ref}",
      "ssh_url": "git@github.com:danira1349/suka_blyat.git",
      "svn_url": "https://github.com/danira1349/suka_blyat",
      "contributors_url": "https://api.github.com/repos/danira1349/suka_blyat/contributors",
      "private": false,
      "subscription_url": "https://api.github.com/repos/danira1349/suka_blyat/subscription",
      "has_projects": true,
      "git_commits_url": "https://api.github.com/repos/danira1349/suka_blyat/git/commits{/sha}",
      "open_issues_count": 0,
      "pulls_url": "https://api.github.com/repos/danira1349/suka_blyat/pulls{/number}",
      "milestones_url": "https://api.github.com/repos/danira1349/suka_blyat/milestones{/number}",
      "size": 14,
      "events_url": "https://api.github.com/repos/danira1349/suka_blyat/events",
      "created_at": "2017-01-27T20:43:31Z",
      "assignees_url": "https://api.github.com/repos/danira1349/suka_blyat/assignees{/user}",
      "forks_count": 0,
      "issue_events_url": "https://api.github.com/repos/danira1349/suka_blyat/issues/events{/number}",
      "hooks_url": "https://api.github.com/repos/danira1349/suka_blyat/hooks",
      "git_refs_url": "https://api.github.com/repos/danira1349/suka_blyat/git/refs{/sha}",
      "owner": {
        "subscriptions_url": "https://api.github.com/users/danira1349/subscriptions",
        "type": "User",
        "followers_url": "https://api.github.com/users/danira1349/followers",
        "id": 16647335,
        "organizations_url": "https://api.github.com/users/danira1349/orgs",
        "gravatar_id": "",
        "events_url": "https://api.github.com/users/danira1349/events{/privacy}",
        "url": "https://api.github.com/users/danira1349",
        "gists_url": "https://api.github.com/users/danira1349/gists{/gist_id}",
        "login": "danira1349",
        "repos_url": "https://api.github.com/users/danira1349/repos",
        "avatar_url": "https://avatars2.githubusercontent.com/u/16647335?v=3",
        "following_url": "https://api.github.com/users/danira1349/following{/other_user}",
        "html_url": "https://github.com/danira1349",
        "site_admin": false,
        "starred_url": "https://api.github.com/users/danira1349/starred{/owner}{/repo}",
        "received_events_url": "https://api.github.com/users/danira1349/received_events"
      },
      "homepage": null,
      "notifications_url": "https://api.github.com/repos/danira1349/suka_blyat/notifications{?since,all,participating}",
      "updated_at": "2017-01-27T20:43:31Z",
      "issue_comment_url": "https://api.github.com/repos/danira1349/suka_blyat/issues/comments{/number}",
      "default_branch": "master",
      "subscribers_url": "https://api.github.com/repos/danira1349/suka_blyat/subscribers",
      "git_tags_url": "https://api.github.com/repos/danira1349/suka_blyat/git/tags{/sha}",
      "blobs_url": "https://api.github.com/repos/danira1349/suka_blyat/git/blobs{/sha}",
      "trees_url": "https://api.github.com/repos/danira1349/suka_blyat/git/trees{/sha}",
      "id": 80244402,
      "languages_url": "https://api.github.com/repos/danira1349/suka_blyat/languages",
      "mirror_url": null,
      "deployments_url": "https://api.github.com/repos/danira1349/suka_blyat/deployments",
      "score": 10.413984,
      "has_issues": true,
      "issues_url": "https://api.github.com/repos/danira1349/suka_blyat/issues{/number}",
      "contents_url": "https://api.github.com/repos/danira1349/suka_blyat/contents/{+path}",
      "has_downloads": true,
      "name": "suka_blyat",
      "labels_url": "https://api.github.com/repos/danira1349/suka_blyat/labels{/name}",
      "forks": 0,
      "watchers": 0,
      "clone_url": "https://github.com/danira1349/suka_blyat.git",
      "comments_url": "https://api.github.com/repos/danira1349/suka_blyat/comments{/number}",
      "open_issues": 0,
      "description": "test for git",
      "watchers_count": 0,
      "commits_url": "https://api.github.com/repos/danira1349/suka_blyat/commits{/sha}",
      "stargazers_count": 0,
      "collaborators_url": "https://api.github.com/repos/danira1349/suka_blyat/collaborators{/collaborator}",
      "keys_url": "https://api.github.com/repos/danira1349/suka_blyat/keys{/key_id}",
      "forks_url": "https://api.github.com/repos/danira1349/suka_blyat/forks",
      "teams_url": "https://api.github.com/repos/danira1349/suka_blyat/teams",
      "has_wiki": true,
      "stargazers_url": "https://api.github.com/repos/danira1349/suka_blyat/stargazers",
      "fork": false
    },
    {
      "compare_url": "https://api.github.com/repos/RaccoonCO/Math/compare/{base}...{head}",
      "downloads_url": "https://api.github.com/repos/RaccoonCO/Math/downloads",
      "language": null,
      "releases_url": "https://api.github.com/repos/RaccoonCO/Math/releases{/id}",
      "statuses_url": "https://api.github.com/repos/RaccoonCO/Math/statuses/{sha}",
      "branches_url": "https://api.github.com/repos/RaccoonCO/Math/branches{/branch}",
      "has_pages": false,
      "pushed_at": "2017-02-28T17:24:30Z",
      "git_url": "git://github.com/RaccoonCO/Math.git",
      "url": "https://api.github.com/repos/RaccoonCO/Math",
      "tags_url": "https://api.github.com/repos/RaccoonCO/Math/tags",
      "full_name": "RaccoonCO/Math",
      "merges_url": "https://api.github.com/repos/RaccoonCO/Math/merges",
      "html_url": "https://github.com/RaccoonCO/Math",
      "archive_url": "https://api.github.com/repos/RaccoonCO/Math/{archive_format}{/ref}",
      "ssh_url": "git@github.com:RaccoonCO/Math.git",
      "svn_url": "https://github.com/RaccoonCO/Math",
      "contributors_url": "https://api.github.com/repos/RaccoonCO/Math/contributors",
      "private": false,
      "subscription_url": "https://api.github.com/repos/RaccoonCO/Math/subscription",
      "has_projects": true,
      "git_commits_url": "https://api.github.com/repos/RaccoonCO/Math/git/commits{/sha}",
      "open_issues_count": 0,
      "pulls_url": "https://api.github.com/repos/RaccoonCO/Math/pulls{/number}",
      "milestones_url": "https://api.github.com/repos/RaccoonCO/Math/milestones{/number}",
      "size": 6589,
      "events_url": "https://api.github.com/repos/RaccoonCO/Math/events",
      "created_at": "2017-02-28T14:05:53Z",
      "assignees_url": "https://api.github.com/repos/RaccoonCO/Math/assignees{/user}",
      "forks_count": 0,
      "issue_events_url": "https://api.github.com/repos/RaccoonCO/Math/issues/events{/number}",
      "hooks_url": "https://api.github.com/repos/RaccoonCO/Math/hooks",
      "git_refs_url": "https://api.github.com/repos/RaccoonCO/Math/git/refs{/sha}",
      "owner": {
        "subscriptions_url": "https://api.github.com/users/RaccoonCO/subscriptions",
        "type": "Organization",
        "followers_url": "https://api.github.com/users/RaccoonCO/followers",
        "id": 26064525,
        "organizations_url": "https://api.github.com/users/RaccoonCO/orgs",
        "gravatar_id": "",
        "events_url": "https://api.github.com/users/RaccoonCO/events{/privacy}",
        "url": "https://api.github.com/users/RaccoonCO",
        "gists_url": "https://api.github.com/users/RaccoonCO/gists{/gist_id}",
        "login": "RaccoonCO",
        "repos_url": "https://api.github.com/users/RaccoonCO/repos",
        "avatar_url": "https://avatars3.githubusercontent.com/u/26064525?v=3",
        "following_url": "https://api.github.com/users/RaccoonCO/following{/other_user}",
        "html_url": "https://github.com/RaccoonCO",
        "site_admin": false,
        "starred_url": "https://api.github.com/users/RaccoonCO/starred{/owner}{/repo}",
        "received_events_url": "https://api.github.com/users/RaccoonCO/received_events"
      },
      "homepage": null,
      "notifications_url": "https://api.github.com/repos/RaccoonCO/Math/notifications{?since,all,participating}",
      "updated_at": "2017-02-28T14:05:53Z",
      "issue_comment_url": "https://api.github.com/repos/RaccoonCO/Math/issues/comments{/number}",
      "default_branch": "master",
      "subscribers_url": "https://api.github.com/repos/RaccoonCO/Math/subscribers",
      "git_tags_url": "https://api.github.com/repos/RaccoonCO/Math/git/tags{/sha}",
      "blobs_url": "https://api.github.com/repos/RaccoonCO/Math/git/blobs{/sha}",
      "trees_url": "https://api.github.com/repos/RaccoonCO/Math/git/trees{/sha}",
      "id": 83439426,
      "languages_url": "https://api.github.com/repos/RaccoonCO/Math/languages",
      "mirror_url": null,
      "deployments_url": "https://api.github.com/repos/RaccoonCO/Math/deployments",
      "score": 5.7899513,
      "has_issues": true,
      "issues_url": "https://api.github.com/repos/RaccoonCO/Math/issues{/number}",
      "contents_url": "https://api.github.com/repos/RaccoonCO/Math/contents/{+path}",
      "has_downloads": true,
      "name": "Math",
      "labels_url": "https://api.github.com/repos/RaccoonCO/Math/labels{/name}",
      "forks": 0,
      "watchers": 0,
      "clone_url": "https://github.com/RaccoonCO/Math.git",
      "comments_url": "https://api.github.com/repos/RaccoonCO/Math/comments{/number}",
      "open_issues": 0,
      "description": "AAAA SUKA BLYAT' NIHYJAA NE PANIMAJY",
      "watchers_count": 0,
      "commits_url": "https://api.github.com/repos/RaccoonCO/Math/commits{/sha}",
      "stargazers_count": 0,
      "collaborators_url": "https://api.github.com/repos/RaccoonCO/Math/collaborators{/collaborator}",
      "keys_url": "https://api.github.com/repos/RaccoonCO/Math/keys{/key_id}",
      "forks_url": "https://api.github.com/repos/RaccoonCO/Math/forks",
      "teams_url": "https://api.github.com/repos/RaccoonCO/Math/teams",
      "has_wiki": true,
      "stargazers_url": "https://api.github.com/repos/RaccoonCO/Math/stargazers",
      "fork": false
    }
  ]
    :return:
    """

async def get_repos(criteria, loop=None):
    response = await search_repos(search_criteria=criteria, loop=loop)
    return {'search_term': criteria,
            'repos': [
                {
                    'name': repo['full_name'],
                    'created_at': repo['created_at'].replace('T', ' ').replace('Z', ' '),
                    'owner_url': repo['owner']['url'],
                    'avatar_url': repo['owner']['avatar_url'],
                    'owner_login': repo['owner']["login"],
                    'sha': 'sha',
                    'commit_message': 'text',
                    'commit_author_name': 'name',

                } for repo in response['items']
            ]}


# @aiohttp_jinja2.template('template.html')
async def navigator_handle(request):
    name = request.match_info.get('search_term')
    if name is None:
        return aiohttp.web.Response(text='Please enter criteria')
    resp = await get_repos(criteria=name, loop=request.app.loop)
    text = "Hello, Dude, U searched for '{}'".format(name)
    import logging
    logging.critical(text)
    from pprint import pprint
    pprint(resp)
    # return aiohttp.web.Response(text=resp)
    # return aiohttp.web.json_response(resp)
    return aiohttp_jinja2.render_template('template.html', request, resp)
    # return resp


def init_front(loop):
    app = aiohttp.web.Application(loop=loop)
    import aiohttp_jinja2
    import jinja2

    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(searchpath='./'))
    app.router.add_get('/navigator/{search_term}', navigator_handle)
    aiohttp.web.run_app(app, loop=loop)
