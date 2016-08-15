import re


def _match(regex, input_str):
    match = re.match(regex, input_str)
    if match:
        return match.groupdict()
    return None


def parse_pull_link(pr_link):
    # ex: https://github.com/OrgName/repo-name/pull/1
    return _match(
        r'https?://github.com/(?P<github_org>[^/]+)/(?P<github_repo>[^/]+)/'
        r'pull/(?P<github_pr_number>\d+)',
        pr_link)


def parse_git_url(git_url):
    # ex: git@github.com:OrgName/repo-name.git
    return _match(r'git@github.com:(?P<github_org>[^/]+)/(?P<github_repo>[^/]+).git', git_url)


def parse_git_branch(git_branch):
    # ex: origin/pr/387/merge
    return _match(r'[^/]+/pr/(?P<github_pr_number>\d+)', git_branch)


def get_pull_request_dict(env):
    pull_request_dict = {}
    for env_var_name, parser in (
        ('ghprbPullLink', parse_pull_link),
        ('GIT_URL', parse_git_url),
        ('GIT_BRANCH', parse_git_branch),
    ):
        env_var_value = env.get(env_var_name)
        if env_var_value:
            info = parser(env_var_value)
            if info:
                pull_request_dict.update(info)
    return pull_request_dict
