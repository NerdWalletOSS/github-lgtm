import git
import owners
import integrations


def pull_request_ready_to_merge(github_token, org, repo, pr_number, owners_file='OWNERS', options=None):
    """
    Using the GitHub API, check whether a pull request is ready to be merged. Adds a comment to the
    pull request that tags anyone who owns a file in the diff.
    :param github_token: A GitHub API token, used to read information and add a comment.
    :param org: A string name of the GitHub organization that owns the repository.
    :param repo: A string name of the GitHub repository for this pull request.
    :param pr_number: An integer ID for the GitHub pull request.
    :param owners_file: A relative path inside the repository where the OWNERS file is defined.
    :param options: Dict of options to be used
    :return: A boolean that represents whether the pull request can be merged.
    """
    options = options or {}
    github_repo = git.GitHub(github_token=github_token, org_name=org, repo_name=repo)
    pull_request = github_repo.get_pull_request(pr_number=pr_number)
    owner_lines = github_repo.read_file_lines(file_path=owners_file)
    owner_ids_and_globs = owners.parse(owner_lines)
    reviewers, required = owners.get_owners_of_files(owner_ids_and_globs, pull_request.files)
    individual_reviewers = github_repo.expand_teams(reviewers, except_login=pull_request.author)
    # individual_reviewers.append(pull_request.get_reviewers(owners_lines=['foo *.js', ]))
    if individual_reviewers:
        if not options.get('skip_assignment'):
            pull_request.assign_to(individual_reviewers[0])

        if pull_request.base_branch not in options.get('skip_notification_branches', []):
            comment = pull_request.generate_comment(reviewers=individual_reviewers, required=required)
            pull_request.create_or_update_comment(comment)

    if pull_request.base_branch in options.get('skip_approval_branches', []):
        return True

    if required:
        return pull_request.all_have_signed_off(required)
    return pull_request.one_has_signed_off(individual_reviewers)


__all__ = [
    'pull_request_ready_to_merge',
    'GitHub',
    'integrations',
]
