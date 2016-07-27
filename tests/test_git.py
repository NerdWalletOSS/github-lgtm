import mock_github
from base import MockPyGithubTests
from lgtm import git


class GitTests(MockPyGithubTests):

    def test_get_team_members(self):
        mock_github.create_fake_org(teams=[mock_github.MockTeam('team1', ['bat', 'baz'])])
        git_hub = git.GitHub('foo', 'bar', 'bat')
        self.assertEquals(git_hub.get_team_members('OrgName/team1'), ['bat', 'baz'])

    def test_expand_teams(self):
        mock_github.create_fake_org(teams=[mock_github.MockTeam('team1', ['bat', 'baz'])])
        git_hub = git.GitHub('foo', 'bar', 'bat')
        self.assertEquals(
            sorted(git_hub.expand_teams(['foo', 'OrgName/team1'])),
            sorted(['foo', 'bat', 'baz']))
