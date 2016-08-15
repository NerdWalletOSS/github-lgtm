import re


def _match(regex, input_str):
    match = re.match(regex, input_str)
    if match:
        return match.groupdict()
    return None


def parse_repo_slug(value):
    # ex: OrgName/repo-name
    return _match(r'(?P<github_org>[^/]+)/(?P<github_repo>[^/]+)', value)


def parse_pull_request(value):
    # ex: '1'
    return {'github_pr_number': int(value)}


def get_pull_request_dict(env):
    pull_request_dict = {}
    for env_var_name, parser in (
        ('TRAVIS_REPO_SLUG', parse_repo_slug),
        ('TRAVIS_PULL_REQUEST', parse_pull_request),
    ):
        env_var_value = env.get(env_var_name)
        if env_var_value:
            info = parser(env_var_value)
            if info:
                pull_request_dict.update(info)
    return pull_request_dict
