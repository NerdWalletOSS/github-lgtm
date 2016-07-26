"""
See: https://www.chromium.org/developers/owners-files

The syntax of the OWNERS file is, roughly:
lines     := (\s* line? \s* "\n")*
line      := directive
          | "per-file" \s+ glob \s* "=" \s* directive
          | comment
directive := "set noparent"
          |  "file:" glob
          |  email_address
          |  "*"
glob      := [a-zA-Z0-9_-*?]+
comment   := "#" [^"\n"]*
"""
import fnmatch
import logging
import utils


logger = logging.getLogger(__name__)


def parse(owners_lines):
    """
    takes a list of lines from a OWNERS text file and returns a list of
    :param owners_lines: a list of strings, one for each line of a OWNERS file
    :return: list of (ID, glob) tuples, where glob can be None
    """
    results = []
    for owner_line in owners_lines:
        # strip the leading @ for github users/teams
        if owner_line.startswith('@'):
            owner_line = owner_line[1:]
        owner_line = owner_line.strip()
        if not owner_line:
            continue
        if owner_line.startswith('#'):
            continue
        if ' ' in owner_line:
            result = tuple(owner_line.split(' ', 1))
        else:
            result = (owner_line, None)
        results.append(result)
    return results


def get_owners_of_files(owner_glob_tuple_list, files):
    """
    Given a list of (ID, glob) tuples and a list of files, return the set of IDs of reviewers
    :param owner_glob_tuple_list: a list of (ID, glob) tuples from OWNERS
    :param files: a list of files changed by the pull request
    :return: the list of IDs of reviewers who should review the PR, and a list of IDs that MUST
        sign off on a PR before it can be merged
    """
    # no ordered set in Python, use ordered dict w/ throw-away key
    # preserve order of input b/c we want to assign PR to first owner
    reviewers, required = list(), list()
    for owner, glob in owner_glob_tuple_list:
        if glob:
            matched_files = fnmatch.filter(files, glob)
            if matched_files:
                logger.debug('%s matches %r' % (owner, matched_files))
                reviewers.append(owner)
                required.append(owner)
        else:
            logger.debug('%s matches anything' % owner)
            reviewers.append(owner)
    return utils.ordered_set(reviewers), utils.ordered_set(required)
