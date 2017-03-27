import json
import requests


def headers(auth_phrase):
    return {
        'Authorization': 'Basic {}'.format(auth_phrase)
    }


def get_teams(auth_phrase):
    try:
        resp = requests.get("https://api.bitbucket.org/2.0/teams/?role=member",
                            headers=headers(auth_phrase)).json()
    except ValueError:
        return None
    return [
        item["username"]
        for item in resp['values']
    ]


def page_all(url, headers, extractor):
    try:
        results = []
        num_results = 1
        page = 1
        while len(results) < num_results:
            resp = (requests.get('{}page={}'.format(url, page), headers=headers)
                    .json())
            num_results = resp['size']
            results += [
                extractor(item)
                for item in resp['values']
            ]
            page += 1
    except ValueError:
        return None
    return results


def get_projects(team, auth_phrase):
    return page_all(
        "https://api.bitbucket.org/2.0/teams/{}/projects/?".format(team),
        headers(auth_phrase),
        lambda item: '{}'.format(item['key'])
    )


def get_team_repositories(team, auth_phrase):
    projects = get_projects(team, auth_phrase)
    team_repositories = []

    for project in projects:
        print("Getting {}/{} repositories...".format(team, project))
        team_repositories += get_project_repositories(team, project, auth_phrase)

    return team_repositories


def get_project_repositories(team, project, auth_phrase):
    return page_all(
        'https://api.bitbucket.org/2.0/repositories/{}?q=project.key="{}"&'.format(team, project),
        headers(auth_phrase),
        lambda item: '{}'.format(item['full_name'])
    )
