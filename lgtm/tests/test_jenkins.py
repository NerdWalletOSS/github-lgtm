from base import MockPyGithubTests
from lgtm.integrations import jenkins


class JenkinsIntegrationTests(MockPyGithubTests):

    def test_get_pull_request_dict(self):
        self.assertEquals(
            jenkins.get_pull_request_dict({
                'ghprbPullLink': 'https://github.com/OrgName/repo-name/pull/387',
            }),
            dict(github_org='OrgName', github_repo='repo-name', github_pr_number='387'))

    def test_get_pull_request_dict_rerun(self):
        self.assertEquals(
            jenkins.get_pull_request_dict({
                'GIT_URL': 'git@github.com:OrgName/repo-name.git',
                'GIT_BRANCH': 'origin/pr/387/merge',
            }),
            dict(github_org='OrgName', github_repo='repo-name', github_pr_number='387'))

    def test_parse_pull_link(self):
        self.assertEquals(
            jenkins.parse_pull_link('https://github.com/OrgName/repo-name/pull/1'),
            dict(github_org='OrgName', github_repo='repo-name', github_pr_number='1'))

    def test_parse_pull_link_bad(self):
        self.assertEquals(jenkins.parse_pull_link('foobar'), None)

    def test_parse_git_url(self):
        self.assertEquals(
            jenkins.parse_git_url('git@github.com:OrgName/repo-name.git'),
            dict(github_org='OrgName', github_repo='repo-name'))

    def test_parse_git_url_bar(self):
        self.assertEquals(jenkins.parse_git_url('foobar'), None)

    def test_parse_git_branch(self):
        self.assertEquals(
            jenkins.parse_git_branch('origin/pr/387/merge'),
            dict(github_pr_number='387'))

    def test_parse_git_branch_bad(self):
        self.assertEquals(
            jenkins.parse_git_branch('foobar'),
            None)
