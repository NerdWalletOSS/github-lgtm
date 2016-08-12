import mock

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

    @mock.patch('lgtm.git.PullRequest.assign_to')
    def test_fails_when_not_ready(self, assigned_to_someone):
        mock_github.create_fake_repo(file_contents={'OWNERS': '@bar'})
        mock_github.create_fake_pull_request(author='blah', comments=[])
        self.assertFalse(pull_request_ready_to_merge(pr_number=1))
        self.assertTrue(assigned_to_someone.called)

    def test_passes_when_approval_not_required(self):
        mock_github.create_fake_repo(file_contents={'OWNERS': '@bar'})
        mock_github.create_fake_pull_request(author='blah', comments=[])
        self.assertTrue(pull_request_ready_to_merge(pr_number=1, options={'skip_approval_branches': ['master']}))

    def test_fails_when_branch_approval_not_required(self):
        mock_github.create_fake_repo(file_contents={'OWNERS': '@bar'})
        mock_github.create_fake_pull_request(author='blah', comments=[])
        self.assertFalse(pull_request_ready_to_merge(pr_number=1, options={'skip_approval_branches': ['develop']}))

    def test_fails_when_branch_does_not_match_skip_list(self):
        mock_github.create_fake_repo(file_contents={'OWNERS': '@bar'})
        mock_github.create_fake_pull_request(author='blah', comments=[])
        self.assertFalse(pull_request_ready_to_merge(pr_number=1, options={'skip_approval_branches': ['develop']}))

    @mock.patch('lgtm.git.PullRequest.generate_comment')
    def test_send_notification_when_branch_does_not_match(self, comment_generated):
        mock_github.create_fake_repo(file_contents={'OWNERS': '@bar'})
        mock_github.create_fake_pull_request(author='blah', comments=[])
        pull_request_ready_to_merge(pr_number=1, options={'skip_notification_branches': ['develop']})
        self.assertTrue(comment_generated.called)

    @mock.patch('lgtm.git.PullRequest.generate_comment')
    def test_skip_notification_when_branch_matches(self, comment_generated):
        mock_github.create_fake_repo(file_contents={'OWNERS': '@bar'})
        mock_github.create_fake_pull_request(author='blah', comments=[])
        pull_request_ready_to_merge(pr_number=1, options={'skip_notification_branches': ['master']})
        self.assertFalse(comment_generated.called)

    @mock.patch('lgtm.git.PullRequest.assign_to')
    def test_skip_assignment(self, assigned_to_someone):
        mock_github.create_fake_repo(file_contents={'OWNERS': '@bar'})
        mock_github.create_fake_pull_request(author='blah', comments=[])
        pull_request_ready_to_merge(pr_number=1, options={'skip_assignment': True})
        self.assertFalse(assigned_to_someone.called)
