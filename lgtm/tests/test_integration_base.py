from base import MockPyGithubTests
from lgtm.integrations import base


class IntegrationBaseTests(MockPyGithubTests):

    def test_get_options_defaults_dict_jenkins(self):
        self.assertEquals(base.get_options_defaults_dict('jenkins', env={}), {})

    def test_get_options_defaults_dict_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            base.get_options_defaults_dict('foobar')
