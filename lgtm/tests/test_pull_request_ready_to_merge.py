from functools import partial

from github import UnknownObjectException

import mock_github
from base import MockPyGithubTests
from lgtm import pull_request_ready_to_merge as pull_request_ready_to_merge_


pull_request_ready_to_merge = partial(pull_request_ready_to_merge_, 'foo', 'bar', 'bat')


class PullRequestReadyToMergeTests(MockPyGithubTests):

    def test_ready(self):
        mock_github.create_fake_pull_request(id=1)
        self.assertTrue(pull_request_ready_to_merge(pr_number=1))

    def test_404(self):
        mock_github.create_fake_pull_request(id=1)
        with self.assertRaises(UnknownObjectException):
            self.assertTrue(pull_request_ready_to_merge(pr_number=2))

    def test_empty_owners_file(self):
        mock_github.create_fake_repo(file_contents={'OWNERS': ''})
        mock_github.create_fake_pull_request(id=1, comments=[])
        self.assertTrue(pull_request_ready_to_merge(pr_number=1))

    def test_no_reviewers_for_these_files(self):
        mock_github.create_fake_repo(file_contents={'OWNERS': '@bar *.js'})
        mock_github.create_fake_pull_request(id=1, file_paths=['file1.txt'])
        self.assertTrue(pull_request_ready_to_merge(pr_number=1))

    def test_single_owner_is_pr_author(self):
        mock_github.create_fake_repo(file_contents={'OWNERS': '@bar'})
        mock_github.create_fake_pull_request(author='bar', comments=[])
        self.assertTrue(pull_request_ready_to_merge(pr_number=1))

    def test_owner_with_no_at_symbol(self):
        mock_github.create_fake_repo(file_contents={'OWNERS': 'bar'})
        mock_github.create_fake_pull_request(author='bar', comments=[])
        self.assertTrue(pull_request_ready_to_merge(pr_number=1))
