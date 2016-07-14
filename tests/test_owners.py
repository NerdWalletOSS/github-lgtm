import unittest

from lgtm import owners


class GetOwnersTests(unittest.TestCase):

    def test_get_owners_of_files(self):
        self.assertEquals(
            owners.get_owners_of_files([('foo', None)], files=['bar', 'bat']),
            ['foo'])

    def test_get_owners_of_files_empty(self):
        self.assertEquals(
            owners.get_owners_of_files([], files=['bar', 'bat']),
            [])

    def test_get_owners_of_files_glob(self):
        self.assertEquals(
            owners.get_owners_of_files([('foo', '*.js')], files=['bar/bat.js']),
            ['foo'])

    def test_get_owners_of_files_glob_subdir(self):
        self.assertEquals(
            owners.get_owners_of_files([('foo', '*/bar/*')], files=['bat/bar/baz.js']),
            ['foo'])


class OwnersParseTests(unittest.TestCase):

    def test_parse(self):
        id_glob_tuples = owners.parse([
            '@github-user',
            '@OrgName/team-name',
            '@github-user2 *.js',
            '@github-user3 */subdir/*',
        ])
        self.assertEquals(id_glob_tuples, [
            ('github-user', None),
            ('OrgName/team-name', None),
            ('github-user2', '*.js'),
            ('github-user3', '*/subdir/*'),
        ])
