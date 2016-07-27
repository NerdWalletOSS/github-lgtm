import mock
import unittest

import mock_github


class MockPyGithubTests(unittest.TestCase):

    def setUp(self):
        github_patcher = mock.patch('lgtm.git.PyGithub', mock_github.MockPyGithub)
        github_patcher.start()
        self.addCleanup(github_patcher.stop)
        self.org = mock_github.create_fake_org()
        self.repo = mock_github.create_fake_repo()
        super(MockPyGithubTests, self).setUp()
