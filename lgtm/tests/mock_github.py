from dateutil import parser as dateutil_parser
from github import UnknownObjectException
from github.PullRequestPart import PullRequestPart


_org_state = {
    'name': None,
    'current_user_login': None,
    'teams': [],
}


def create_fake_org(**kwargs):
    defaults = dict(
        org_name='OrgName',
        current_user_login='bot',
        teams=[
            MockTeam('team1', ['bat', 'baz']),
        ],
    )
    defaults.update(kwargs)
    global _org_state
    _org_state.update(defaults)


_repo_state = {
    'name': None,
    'file_contents': {},
}


def create_fake_repo(**kwargs):
    defaults = dict(
        name='repo-name',
        file_contents={
            'OWNERS': '@foo\n'
                      '@bar *.js\n'
                      '@OrgName/team1 build/*\n'
            },
    )
    defaults.update(kwargs)
    global _repo_state
    _repo_state.update(defaults)


_pull_request_state = {}


def create_fake_pull_request(**kwargs):
    defaults = dict(
        id=1,
        author='bat',
        last_commit_date='2016-01-01 00:00:01',
        file_paths=[
            'file1',
            'file2.js'
            'build/foo.txt',
        ],
        comments=[
            ('2016-01-01 00:00:00', 'foo', 'lgtm'),  # too early
            ('2016-01-01 00:00:02', 'bat', 'lgtm'),  # from the author
            ('2016-01-01 00:00:03', 'boo', 'lgtm'),  # not from an owner
            ('2016-01-01 00:00:04', 'baz', 'some comment'),  # not an lgtm comment
            ('2016-01-01 00:00:05', 'foo', 'lgtm'),  # this one is a successful lgtm
        ],
    )
    defaults.update(kwargs)
    global _pull_request_state
    _pull_request_state = {defaults.get('id'): defaults}


class MockPyGithub(object):

    def __init__(self, login_or_token):
        self.login_or_token = login_or_token

    def get_organization(self, login):
        # TODO: check that this org name is correct
        return MockOrganization(login)

    def get_user(self, login=None):
        login = login or _org_state['current_user_login']
        return MockUser(login)


class MockUser(object):

    def __init__(self, login):
        self.login = login
        self.name = login


class MockTeam(object):

    def __init__(self, name, member_logins=None):
        self.name = name
        self.member_logins = member_logins or []

    def get_members(self):
        return [MockUser(login) for login in self.member_logins]


class MockOrganization(object):

    def __init__(self, login):
        self.login = login

    def get_repo(self, full_name_or_id, lazy=True):
        return MockRepository(full_name_or_id)

    def get_teams(self):
        return _org_state['teams']


class MockRepository(object):

    def __init__(self, full_name_or_id):
        self.full_name_or_id = full_name_or_id

    def get_pull(self, number):
        if number not in _pull_request_state:
            raise UnknownObjectException(404, 'not found')
        return MockPullRequest.from_state(id=number)

    def get_issue(self, number):
        if number not in _pull_request_state:
            raise UnknownObjectException(404, 'not found')
        return MockIssue()

    def get_file_contents(self, path, ref=None):
        if path not in _repo_state['file_contents']:
            raise UnknownObjectException(404, 'not found')
        return MockFileContents(_repo_state['file_contents'].get(path))


class MockFileContents(object):

    def __init__(self, contents):
        self.decoded_content = contents


class MockPullRequest(object):

    def __init__(self, id, author, last_commit_date, file_paths, comments, **kwargs):
        self._id = id
        self._author = author
        self._last_commit_date_str = last_commit_date
        self._last_commit_date = dateutil_parser.parse(last_commit_date)
        self._file_paths = file_paths
        self._comments = comments
        self.base = PullRequestPart(None, None, {"ref": "master"}, False)

    @classmethod
    def from_state(cls, id):
        return cls(**_pull_request_state.get(id))

    @property
    def user(self):
        return MockUser(self._author)

    def get_issue_comments(self):
        return [MockComment(*comment) for comment in self._comments]

    def create_issue_comment(self, body):
        pass

    def get_files(self):
        return [MockFile(f) for f in self._file_paths]

    def get_commits(self):
        # don't need anything except the most recent date
        return [MockCommit(self._last_commit_date_str), ]


class MockCommit(object):

    def __init__(self, last_modified):
        self.last_modified = last_modified


class MockFile(object):

    def __init__(self, filename):
        self.filename = filename


class MockComment(object):

    def __init__(self, created_at, login, body):
        self.created_at = dateutil_parser.parse(created_at)
        self.user = MockUser(login)
        self.body = body


class MockIssue(object):

    def __init__(self):
        self.assignee = None

    def edit(self, assignee):
        self.assignee = assignee
