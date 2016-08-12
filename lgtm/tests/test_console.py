import mock_github
from base import MockPyGithubTests
from lgtm import console


class ConsoleTests(MockPyGithubTests):

    def test_get_options_parser(self):
        options = console.get_options_parser([
            '--github-token',
            'foo',
            '--github-org',
            'OrgName',
            '--github-repo',
            'repo-name',
            '--github-pr-number',
            '1',
            '--skip-approval',
            'master',
            '--skip-approval',
            'develop',
            '--skip-notification',
            'master',
            '--skip-assignment',
        ], do_exit=False)
        self.assertEquals(options.github_token, 'foo')
        self.assertEquals(options.github_org, 'OrgName')
        self.assertEquals(options.github_repo, 'repo-name')
        self.assertEquals(options.github_pr_number, 1)
        self.assertItemsEqual(options.skip_notification_branches, ['master'])
        self.assertItemsEqual(options.skip_approval_branches, ['master', 'develop'])
        self.assertTrue(options.skip_assignment)

    def test_main_ready(self):
        mock_github.create_fake_pull_request(id=1)
        console.main([
            '--github-token',
            'foo',
            '--github-org',
            'OrgName',
            '--github-repo',
            'repo-name',
            '--github-pr-number',
            '1',
        ], do_exit=False)

    def test_main_not_ready(self):
        mock_github.create_fake_repo(name='repo-name', file_contents={
            'OWNERS': 'some-other-person'
            })
        mock_github.create_fake_pull_request(id=1)
        console.main([
            '--github-token',
            'foo',
            '--github-org',
            'OrgName',
            '--github-repo',
            'repo-name',
            '--github-pr-number',
            '1',
        ], do_exit=False)

    def test_main_version(self):
        console.main([
            '--version',
        ], do_exit=False)
