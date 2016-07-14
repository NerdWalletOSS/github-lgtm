import git


def pull_request_ready_to_merge(github_token, org, repo, pr_number, owners_file='OWNERS'):
    """
    Using the GitHub API, check whether a pull request is ready to be merged. Adds a comment to the
    pull request that tags anyone who owns a file in the diff.
    :param github_token: A GitHub API token, used to read information and add a comment.
    :param org: A string name of the GitHub organization that owns the repository.
    :param repo: A string name of the GitHub repository for this pull request.
    :param pr_number: An integer ID for the GitHub pull request.
    :param owners_file: A relative path inside the repository where the OWNERS file is defined.
    :return: A boolean that represents whether the pull request can be merged.
    """
    github_repo = git.GitHub(github_token=github_token, org_name=org, repo_name=repo)
    pull_request = github_repo.get_pull_request(pr_number=pr_number)
    reviewers = pull_request.get_reviewers(owners_file=owners_file)
    # reviewers.append(pull_request.get_reviewers(owners_lines=['foo *.js', ]))
    pull_request.assign_to(reviewers)
    return pull_request.ready_to_merge(reviewers)


__all__ = [
    'pull_request_ready_to_merge',
    'GitHub',
]
