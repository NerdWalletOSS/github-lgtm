# GitHub LGTM

github-lgtm is a pull request approval system using GitHub
[protected branches](https://help.github.com/articles/about-protected-branches/)
and [OWNERS](https://www.chromium.org/developers/owners-files) files.


## Quickstart

```bash
pip install lgtm
lgtm --github-token=MY_TOKEN --github-org=OrgName --github-repo=repo-name --github-pr-number=1
```

## How it Works

1. Create an `OWNERS` file as defined in the "Configuration" section
2. Create a GitHub webhook that runs the `lgtm` check on pull requests.
3. Lock down the GitHub repo to prevent merging without successful checks.
4. Reviewers will be automatically notified when they need to sign off on a pull request.

![mention](https://dl.dropboxusercontent.com/spa/sffu0th1cc1sg9q/mo8dberl.png)

5. Reviewers leave a "lgtm" comment on the pull request to sign off on a change.

![lgtm](https://dl.dropboxusercontent.com/spa/sffu0th1cc1sg9q/cwa6vv73.png)

6. Once the required set of reviewers has signed off, the pull request be eligible to be merged.

![checks](https://help.github.com/assets/images/help/repository/req-status-check-all-passed.png)


Behavior:

- If there is no `OWNERS` file, all pull requests may be merged immediately.
- If there is an `OWNERS` file, but no reviewers for the set of files on the PR,
  the  pull request may be merged immediately.
- If you are the single owner in a repo, there is no need to sign off on your own PRs.
- Any commit will invalidate any existing sign offs; they must be made again.


## Configuration

Configuring who is notified when a PR is opened, and who has has to sign off on what files, is
controlled entirely through the text file `OWNERS` in the root of your repository.

Example:

```bash
@github-user
@OrgName/team-name
@github-user2 *.js
@github-user3 */subdir/*
```

In this example, `@github-user` owns any file that changes in this repo. They will be notified, and
are eligible to single-handedly sign off on a pull request unless there are files changes that
someone else specifically owns. Anyone in the team `@OrgName/team-name` will be notified of any
file changing. `@github-user2` owns any javascript file. `@github-user3` owns any file under
any directory named `subdir`, anywhere except in the root of the repo. *Effectively,
`@github-user2` AND `@github-user3` must BOTH sign off any a PR that contains both a Javascript
change and a change to the `subdir` directory.*

**ALL reviewers watching specific files changed in a pull request must sign off before it is merged.**

You can specify the same user in multiple lines if you want to match more than one glob.

*Note:* The file matching uses [glob](https://en.wikipedia.org/wiki/Glob_(programming))
style matching provided by the
[fnmatch](https://docs.python.org/2/library/fnmatch.html#fnmatch.fnmatch) module in python.


## Reviewers and Required Reviewers

When a pull request is opened, `lgtm` will get the list of files that have been changed. It will
run through the users and teams in your `OWNERS` file, and build two lists; a list of reviewers
and a list of required reviewers.

- Reviewers are users or teams who will be notified that a change is taking place.
- Required Reviewers are users or teams who must ALL sign off on a change before it can be merged.

**Note: if there are only reviewers on a pull request, any single one of them may sign off.**

The line `@github-user` in your `OWNERS` file means that this user is a reviewer of the repo. The
line `@github-user *` means that they are specifically watching every file. Effectively, they must
sign off on any change.

Pull request authors are themselves exempt from being a reviewer on their own pull requests.


## Notification

All reviewers and required reviewers will be notified when a pull request is opened by being tagged
with and PR comment, created by the user associated with the `GITHUB_TOKEN`. Only one comment
will be created, the first time the lgtm tool is run.

*Note: you can easily see which pull requests you have been mentioned on by going to
[https://github.com/pulls](https://github.com/pulls)*


## Assignment

Every pull request will assigned to the first matching reviewer from the `OWNERS` file. Order
matters!


## GitHub Teams

You can use teams in your `OWNERS` file with the format `@OrgName/team-name`. If a team is a
reviewer, all individual team members will be notified. This is because the GitHub UI does not
allow you to easily filter down to pull requests that mention a team you are on.

If a team is a required reviewer, any single member of the team can sign off on the pull request
for the entire team.

If the pull request author is on a reviewing team, they are not allowed to sign off. Someone else
on the team will need to sign off.


## Integration

The idea is that you use a continuous integration server to run the `lgtm` tool on every PR, PR
comment or new commit pushed to a PR.


### Jenkins

- Install the [GitHub pull request builder plugin](https://wiki.jenkins-ci.org/display/JENKINS/GitHub+pull+request+builder+plugin)
- Configure the pull request builder as per their instructions
- Install the tool on the Jenkins server with `sudo pip install lgtm`
- Add `GITHUB_TOKEN=foobar lgtm --integration jenkins` to your list of build steps.
- Under `Build Triggers` -> `GitHub Pull Request Builder` -> `Advanced`, set the `Trigger phrase` to `lgtm`.


### Travis

Example `.travis.yml`:

```bash
language: python
python:
  - "2.7"
env:
  secure: ""
install: "pip install lgtm"
script: lgtm --integration travis
```

The `secure` option is used to pass your GitHub API token. You can generate the value by doing
the following:

```bash
gem install travis
travis encrypt GITHUB_TOKEN=foobar
```

That's it! **Note: Travis cannot be trigger to rebuild on new comments. You must manually
re-trigger the build**


## Usage from CLI:

```bash
lgtm --help
```

### Help:

```bash
usage: console.py [-h] [--github-token GITHUB_TOKEN] [--github-org GITHUB_ORG]
                  [--github-repo GITHUB_REPO]
                  [--github-pr-number GITHUB_PR_NUMBER]
                  [--owners-file OWNERS_FILE] [--integration {jenkins,travis}]
                  [--skip-approval <branch_name>] [--skip-assignment]
                  [--skip-notification <branch_name>]
                  [--version] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  --github-token GITHUB_TOKEN
                        GitHub API Token, can also use GITHUB_TOKEN
                        environment variable
  --github-org GITHUB_ORG
                        GitHub organization name
  --github-repo GITHUB_REPO
                        Pull request repository name
  --github-pr-number GITHUB_PR_NUMBER
                        Pull request number
  --owners-file OWNERS_FILE
                        Relative path to OWNERS file
  --integration {jenkins,travis}
                        Extract org/repo/pr from environment variables
                        specific to a platform
  --skip-approval       Add a branch to the list of branches for which
                        approval is not necessary.
  --skip-assignment     Do not assign the PR to anyone on the reviewers
                        list.
  --skip-notification   Add a branch to the list of branches for which
                        notification should not be sent.
  --version             Print version and exit
  --verbose             Print commands that are running and other debug info
```

## Usage from Python:

You can integrate into an existing Python check with just a couple of lines of code.

```python
from lgtm import pull_request_ready_to_merge

if pull_request_ready_to_merge(github_token='MY_TOKEN', org='OrgName', repo='repo-name', pr_number=1):
    pass
```


### Advanced usage:

For more control over the list of reviewers, who is required, whether anyone is assigned to a PR,
etc, you can use this snippet from the definition of `pull_request_ready_to_merge`:

```python
from lgtm import git, owners

github_repo = git.GitHub(github_token=github_token, org_name=org, repo_name=repo)
pull_request = github_repo.get_pull_request(pr_number=pr_number)
owner_lines = github_repo.read_file_lines(file_path=owners_file)
owner_ids_and_globs = owners.parse(owner_lines)
reviewers, required = owners.get_owners_of_files(owner_ids_and_globs, pull_request.files)
individual_reviewers = github_repo.expand_teams(reviewers, except_login=pull_request.author)
# individual_reviewers.append(pull_request.get_reviewers(owners_lines=['foo *.js', ]))
if individual_reviewers:
    pull_request.assign_to(individual_reviewers[0])
    comment = pull_request.generate_comment(reviewers=individual_reviewers, required=required)
    pull_request.create_or_update_comment(comment)
if required and pull_request.all_have_signed_off(required):
    pass
else if pull_request.one_has_signed_off(individual_reviewers):
    pass
```
