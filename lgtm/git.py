import logging

from dateutil import parser as dateutil_parser
from github import Github as PyGithub
from github import UnknownObjectException
import utils


logger = logging.getLogger(__name__)


# prefix to the notification comment, also used to identify the comment during future runs
REVIEW_COMMENT_PREFIX = 'This pull request requires a code review.'
# a list of patterns to match against comments that indicate a successful code review
LGTM_ALIASES = [
    'lgtm',
    ':shipit:',
    ':+1:'
]


class GitHub(object):
    """
    Wrapper around PyGithub with helpers for getting repo owners, a handle to pull request object.
    """

    def __init__(self, github_token, org_name, repo_name):
        self._git_api = PyGithub(github_token)
        self.org_name = org_name
        self.repo_name = repo_name
        self.org = None
        self.repo = None
        self.current_user_login = None

    def _connect(self):
        self.org = self._git_api.get_organization(self.org_name)
        self.repo = self.org.get_repo(self.repo_name)
        self.current_user_login = self._git_api.get_user().name

    def read_file_lines(self, file_path='OWNERS'):
        """
        Get a list of strings, one per line in the file
        :param owners_file: A relative path to the file
        :return: a list of line strings
        """
        self._connect()
        try:
            owner_file_contents = self.repo.get_file_contents(file_path)
            return owner_file_contents.decoded_content.split('\n')
        except UnknownObjectException:
            return []

    def get_pull_request(self, pr_number):
        """
        :param pr_number: A GitHub pull request ID
        :return: Handle to PullRequest helper
        """
        self._connect()
        return PullRequest(self, pr_number)

    def get_team_members(self, team_name):
        """
        Returns a list of GitHub user names for the members of a GitHub team
        :param team_name: GitHub team name, like 'OrgName/team1'
        :return: a list of GitHub user names
        """
        self._connect()
        assert '/' in team_name
        org, team_name = team_name.split('/')  # ex: NerdWallet/dit
        teams = self.org.get_teams()
        teams = [t for t in teams if t.name == team_name]
        if not teams:
            return []
        return [m.login for m in teams[0].get_members()]

    def expand_teams(self, logins_and_teams_list, except_login=None):
        """
        Given a list of GitHub user names and team names, return a set of user names with the team
        members expanded.
        :param logins_and_teams_list: list of GitHub user names and team names
        :return: list of GitHub user names
        """
        self._connect()
        logins = list()
        for login_or_team in logins_and_teams_list:
            if login_or_team == except_login:
                continue
            if '/' in login_or_team:
                for login in self.get_team_members(login_or_team):
                    logins.append(login)
            else:
                logins.append(login_or_team)
        return utils.ordered_set(logins)


class PullRequest(object):
    """
    A helper object for GitHub pull requests that can pull reviews based on an OWNERS file,
    pull comments and author. It can also notify users on the pull request via a comment, and
    determine whether a pull request has been signed off on by the required reviewers.
    """

    def __init__(self, git_hub, pr_number):
        self._git_hub = git_hub
        self.pr_number = pr_number
        self._pr = git_hub.repo.get_pull(self.pr_number)

    @property
    def base_branch(self):
        return self._pr.base.ref

    @property
    def files(self):
        return [f.filename for f in self._pr.get_files()]

    @property
    def comments(self):
        """
        Gets the comments on a pull request.
        :return: a list of (user name, comment text) tuples
        """
        comments = self._pr.get_issue_comments()
        return comments

    @property
    def last_commit_date(self):
        """
        Gets the date of the most recent commit on a pull request.
        :return: a datetime object
        """
        commits = self._pr.get_commits()
        commit_date_strings = [c.last_modified for c in commits]
        commit_dates = [dateutil_parser.parse(d).replace(tzinfo=None) for d in commit_date_strings]
        return max(commit_dates) if commit_dates else None

    @property
    def author(self):
        """
        Get the GitHub user name of the pull request author
        :return: a GitHub user name
        """
        return self._pr.user.login

    def assign_to(self, login):
        """
        Assign a PR to a specific user.

        :param login: A list of GitHub user name
        """
        issue = self._git_hub.repo.get_issue(self.pr_number)
        try:
            issue.edit(assignee=login)
        except UnknownObjectException:
            logger.warn('Cannot assign issue to %r, issue not found' % login)

    def _get_existing_comment(self):
        for comment in self.comments:
            author = comment.user.login
            if author != self._git_hub.current_user_login:
                continue
            if comment.body.startswith(REVIEW_COMMENT_PREFIX):
                return comment
        return None

    def _make_mention_string(self, logins):
        return ' '.join(['@%s' % login for login in logins])

    def generate_comment(self, reviewers, required, prefix=None):
        if not reviewers and not required:
            return None
        prefix = prefix or REVIEW_COMMENT_PREFIX
        message = '%s\n\n' % prefix
        if required:
            message += 'All of the following reviewers must sign off: '
            message += self._make_mention_string(required)
            message += '\n\n'
            message += 'Optional: %s' % self._make_mention_string(reviewers)
        else:
            message += 'One of the following reviewers must sign off: '
            message += self._make_mention_string(reviewers)
        message = message.strip()
        return message

    def create_or_update_comment(self, message):
        """
        Notify a list of GitHub user names that they should review this pull request. Only notifies
        the users once.

        :param reviewers: A list of GitHub user names that should review the PR
        :param required: A list of GitHub user names that are required to review the PR
        :param prefix: A prefix to append to any automated comments
        """
        # see: https://github.com/blog/2178-multiple-assignees-on-issues-and-pull-requests
        # see: https://github.com/PyGithub/PyGithub/issues/404
        if not message:
            return
        existing_comment = self._get_existing_comment()
        if existing_comment:
            if existing_comment.body == message:
                return
            existing_comment.edit(message)
        else:
            self._pr.create_issue_comment(message)

    def one_has_signed_off(self, reviewers):
        if not reviewers:
            return True
        sign_offs = self.signed_off_by()
        for reviewer in reviewers:
            assert '/' not in reviewer, 'Teams of reviewers should be expanded already'
            if reviewer in sign_offs:
                return True
        return False

    def all_have_signed_off(self, required_reviewers):
        if not required_reviewers:
            return True
        sign_offs = self.signed_off_by()
        sign_offs = self._git_hub.expand_teams(sign_offs, except_login=self.author)
        for required_reviewer in required_reviewers:
            if required_reviewer not in sign_offs:
                return False
        return True

    def signed_off_by(self, except_login=None):
        """
        Get the list of GitHub user names who have signed off on the pull request.
        :param except_login: A GitHub user name who should not be allowed to sign off
        :return: A list of GitHub user names
        """
        except_login = except_login or self.author
        lgtm_logins = list()
        last_commit_date = self.last_commit_date
        for comment in self.comments:
            author = comment.user.login
            # do not let the author sign off on their own PR
            if author == except_login:
                continue
            # ignore any lgtm comments prior to the most recent commit (need to lgtm again)
            if last_commit_date and comment.created_at < last_commit_date:
                continue
            comment_body = comment.body.lower()
            for lgtm_token in LGTM_ALIASES:
                # TODO: regex
                if lgtm_token in comment_body:
                    lgtm_logins.append(author)
        return utils.ordered_set(lgtm_logins)
