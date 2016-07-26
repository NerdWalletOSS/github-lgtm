# GitHub LGTM

github-lgtm is a pull request approval system using GitHub
[protected branches](https://help.github.com/articles/about-protected-branches/)
and [OWNERS](https://www.chromium.org/developers/owners-files) files.

## OWNERS files

Start by creating an `OWNERS` files in the root of your repository. Example:

```bash
@github-user
@OrgName/team-name
@github-user2 *.js
@github-user3 */subdir/*
```

In this example, `@github-user` owns any file that changes in this repo. Anyone in the team
`@OrgName/team-name` also owns any file. `@github-user2 ` owns any javascript file, in any
directory. `@github-user3` owns any file under any directory named `subdir`, anywhere except in
the root of the repo.

You can specify the same user in multiple lines if you want to match more than one glob.

*Note:* The file matching uses [glob](https://en.wikipedia.org/wiki/Glob_(programming))
style matching provided by the
[fnmatch](https://docs.python.org/2/library/fnmatch.html#fnmatch.fnmatch) module in python.


## Usage from CLI:

```bash
lgtm --github-token=MY_TOKEN --github-pr-link=https://github.com/OrgName/repo-name/pull/1
```

### Help:

```bash
usage: lgtm  [-h] [--github-token GITHUB_TOKEN]
                  [--github-pr-link GITHUB_PR_LINK] [--github-org GITHUB_ORG]
                  [--github-repo GITHUB_REPO]
                  [--github-pr-number GITHUB_PR_NUMBER]
                  [--owners-file OWNERS_FILE] [--version] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  --github-token GITHUB_TOKEN
                        GitHub API Token, can also use GITHUB_TOKEN
                        environment variable
  --github-pr-link GITHUB_PR_LINK
                        GitHub PR URL, can also use ghprbPullLink environment
                        variable. You can also specify individual settings for
                        org name, repo name and PR number.
  --github-org GITHUB_ORG
                        GitHub organization name
  --github-repo GITHUB_REPO
                        Pull request repository name
  --github-pr-number GITHUB_PR_NUMBER
                        Pull request number
  --owners-file OWNERS_FILE
                        Relative path to OWNERS file
  --version             Print version and exit
  --verbose             Print commands that are running and other debug info
```

## Usage from Python:

```python
from lgtm import pull_request_ready_to_merge

if pull_request_ready_to_merge(github_token='MY_TOKEN', org='OrgName', repo='repo-name', pr_number=1):
    pass
```

### Advanced usage:

```python
from lgtm import GitHub

github_repo = git.GitHub(github_token=github_token, org_name=org, repo_name=repo)
pull_request = github_repo.get_pull_request(pr_number=pr_number)
owner_lines = github_repo.read_file_lines(file_path=owners_file)
owner_ids_and_globs = owners.parse(owner_lines)
reviewers, required = owners.get_owners_of_files(owner_ids_and_globs, pull_request.files)
individual_reviewers = github_repo.expand_teams(reviewers, except_login=pull_request.author)
# individual_reviewers.append(pull_request.get_reviewers(owners_lines=['foo *.js', ]))
if individual_reviewers:
    pull_request.assign_to(individual_reviewers[0])
    pull_request.notify(individual_reviewers)
if required and pull_request.all_have_signed_off(required):
    pass
else if pull_request.one_has_signed_off(individual_reviewers):
    pass
```


## Notification

Any owner on a PR will be notified by being tagged on a PR comment, created by the user associated
with the `GITHUB_TOKEN`. Only one comment will be created, the first time the lgtm tool is run.


## Workflow

The idea is that you use a continuous integration server to run the lgtm tool on every PR, PR
comment or new commit pushed to a PR.

- If there is no `OWNERS` file, `pull_request_ready_to_merge` will return True.
- If there is an `OWNERS` file, but no reviewers for the set of files on the PR,
  `pull_request_ready_to_merge` will return True.
- If you are the single owner in a repo, there is no need to lgtm your own PRs.
- The first reviewer by `OWNER` file order will be assigned on the PR.
- If there are specific teams or individuals who match the PR files list with a specific glob, those
  reviewers are *required*. All individuals and at least one team member must sign off individually.
