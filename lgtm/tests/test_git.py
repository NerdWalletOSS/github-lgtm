import mock_github

from .. import owners

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


class MessageContentTestSuite(MockPyGithubTests):
    def setUp(self):
        super(MessageContentTestSuite, self).setUp()

    def test_make_mention_string_does_sorting(self):
        mock_github.create_fake_repo(file_contents={'OWNERS': '@bar\n@baz *.js\n@blah build/*'})
        mock_github.create_fake_pull_request(author='bar', comments=[])
        github_repo = git.GitHub('foo', 'bar_org', 'bat')
        pr = github_repo.get_pull_request(1)
        owner_lines = github_repo.read_file_lines(file_path='OWNERS')
        owner_ids_and_globs = owners.parse(owner_lines)
        reviewers, required = owners.get_owners_of_files(owner_ids_and_globs, pr.files)
        individual_reviewers = github_repo.expand_teams(reviewers, except_login=pr.author)
        self.assertEqual(pr._make_mention_string(['zika', 'pika', 'aaka', 'aka']), '@aaka @aka @pika @zika')

    def test_message_when_all_required_required_are_removed_from_optional(self):
        mock_github.create_fake_repo(file_contents={'OWNERS': '@bar\n@baz *.js\n@blah build/*'})
        mock_github.create_fake_pull_request(author='bar', comments=[])
        github_repo = git.GitHub('foo', 'bar_org', 'bat')
        pr = github_repo.get_pull_request(1)
        owner_lines = github_repo.read_file_lines(file_path='OWNERS')
        owner_ids_and_globs = owners.parse(owner_lines)
        reviewers, required = owners.get_owners_of_files(owner_ids_and_globs, pr.files)
        individual_reviewers = github_repo.expand_teams(reviewers, except_login=pr.author)
        self.assertItemsEqual(reviewers, ['bar', 'baz', 'blah'])
        self.assertItemsEqual(required, ['baz', 'blah'])
        output = pr.generate_comment(reviewers, required, ' ')
        self.assertEqual(output, 'All of the following reviewers must sign off: @baz @blah')

    def test_message_when_one_required_with_some_optional(self):
        mock_github.create_fake_repo(file_contents={'OWNERS': '@bar\n@baz *.js\n@blah build/*'})
        mock_github.create_fake_pull_request(author='betty', comments=[])
        github_repo = git.GitHub('foo', 'bar_org', 'bat')
        pr = github_repo.get_pull_request(1)
        owner_lines = github_repo.read_file_lines(file_path='OWNERS')
        owner_ids_and_globs = owners.parse(owner_lines)
        reviewers, required = owners.get_owners_of_files(owner_ids_and_globs, pr.files)
        individual_reviewers = github_repo.expand_teams(reviewers, except_login=pr.author)
        self.assertItemsEqual(reviewers, ['bar', 'baz', 'blah'])
        self.assertItemsEqual(required, ['baz', 'blah'])
        output = pr.generate_comment(reviewers, required, ' ')
        self.assertEqual(output, 'All of the following reviewers must sign off: @baz @blah' +
                         '\n\n' + 'Optional: @bar')

    def test_message_when_none_required(self):
        mock_github.create_fake_repo(file_contents={'OWNERS': '@bar\n@baz\n@blah'})
        mock_github.create_fake_pull_request(author='bar', comments=[])
        github_repo = git.GitHub('foo', 'bar_org', 'bat')
        pr = github_repo.get_pull_request(1)
        owner_lines = github_repo.read_file_lines(file_path='OWNERS')
        owner_ids_and_globs = owners.parse(owner_lines)
        reviewers, required = owners.get_owners_of_files(owner_ids_and_globs, pr.files)
        individual_reviewers = github_repo.expand_teams(reviewers, except_login=pr.author)
        self.assertItemsEqual(reviewers, ['bar', 'baz', 'blah'])
        self.assertEqual(required, [])
        output = pr.generate_comment(reviewers, required, ' ')
        self.assertEqual(output, 'One of the following reviewers must sign off: @baz @blah')

    def test_message_when_approval_skipped(self):
        mock_github.create_fake_repo(file_contents={'OWNERS': '@bar\n@baz\n@blah'})
        mock_github.create_fake_pull_request(author='bar', comments=[])
        github_repo = git.GitHub('foo', 'bar_org', 'bat')
        pr = github_repo.get_pull_request(1)
        owner_lines = github_repo.read_file_lines(file_path='OWNERS')
        owner_ids_and_globs = owners.parse(owner_lines)
        reviewers, required = owners.get_owners_of_files(owner_ids_and_globs, pr.files)
        individual_reviewers = github_repo.expand_teams(reviewers, except_login=pr.author)
        self.assertItemsEqual(reviewers, ['bar', 'baz', 'blah'])
        self.assertEqual(required, [])
        output = pr.generate_comment(reviewers, required, ' ', False)
        self.assertEqual(output, 'No approval necessary on this PR.\n/cc @baz @blah')
