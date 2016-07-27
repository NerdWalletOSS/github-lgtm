import unittest

from lgtm import owners


class GetOwnersTests(unittest.TestCase):

    def test_get_owners_of_files(self):
        reviewers, required = owners.get_owners_of_files([('foo', None)], files=['bar', 'bat'])
        self.assertEquals(reviewers, ['foo'])
        self.assertEquals(required, [])

    def test_get_owners_of_files_empty(self):
        reviewers, required = owners.get_owners_of_files([], files=['bar', 'bat'])
        self.assertEquals(reviewers, [])
        self.assertEquals(required, [])

    def test_get_owners_of_files_glob(self):
        reviewers, required = owners.get_owners_of_files([('foo', '*.js')], files=['bar', 'bat.js'])
        self.assertEquals(reviewers, ['foo'])
        self.assertEquals(required, ['foo'])

    def test_get_owners_of_files_glob_subdir(self):
        reviewers, required = owners.get_owners_of_files(
            [('foo', '*/bar/*')], files=['foo/bar/bat'])
        self.assertEquals(reviewers, ['foo'])
        self.assertEquals(required, ['foo'])

    def test_get_owners_of_files_glob_all(self):
        reviewers, required = owners.get_owners_of_files([('foo', '*')], files=['bar', 'bat'])
        self.assertEquals(reviewers, ['foo'])
        self.assertEquals(required, ['foo'])

    def get_owners_of_files_order(self):
        reviewers, required = owners.get_owners_of_files([
                ('foo', None),
                ('bar', '*'),
                ('bat', '*'),
                ('foo', '*'),
                ('foo', '*.js'),
            ], files=['bar', 'bat'])
        self.assertEquals(reviewers, ['foo', 'bar', 'bat'])
        self.assertEquals(required, ['foo'])


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
