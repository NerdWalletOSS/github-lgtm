"""
Command line interface. Parses sys.argv arguments, imports environment variables, executes
pull_request_ready_to_merge() with the supplied parameters, prints any logging output to stdout, and
exits with an appropriate exit code.
"""
import argparse
import logging
import os
import sys
import pkg_resources

from lgtm import pull_request_ready_to_merge


logger = logging.getLogger(__name__)


def get_options_parser(args=None, do_exit=True):
    """
    Parses and validates sys.argv + environment variables into an options object
    :return: the options object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--github-token',
        help='GitHub API Token, can also use GITHUB_TOKEN environment variable',
        default=os.environ.get('GITHUB_TOKEN'))
    parser.add_argument(
        '--github-pr-link',
        help='GitHub PR URL, can also use ghprbPullLink environment variable. You can also '
             'specify individual settings for org name, repo name and PR number.',
        default=os.environ.get('ghprbPullLink'))
    parser.add_argument('--github-org', help='GitHub organization name')
    parser.add_argument('--github-repo', help='Pull request repository name')
    parser.add_argument('--github-pr-number', help='Pull request number')
    parser.add_argument('--owners-file', help='Relative path to OWNERS file', default='OWNERS')
    parser.add_argument('--version', help='Print version and exit', action='store_true')
    parser.add_argument(
        '--verbose',
        help='Print commands that are running and other debug info',
        action='store_true')
    options = parser.parse_args(args)
    if options.github_pr_link:
        # ex: https://github.com/OrgName/repo-name/pull/1
        parts = options.github_pr_link.split('/')
        options.github_org = parts[3]
        options.github_repo = parts[4]
        options.github_pr_number = int(parts[6])
    if not options.github_org or not options.github_repo or not options.github_pr_number:
        parser.print_usage()
        if do_exit:
            exit()
    return options


def log_debug_info(options):
    logger.debug('github_token == %r' % options.github_token)
    logger.debug('github_org == %r' % options.github_org)
    logger.debug('github_repo == %r' % options.github_repo)
    logger.debug('github_pr_number == %r' % options.github_pr_number)
    logger.debug('owners_file == %r' % options.owners_file)


def main(args=None, do_exit=True):
    """
    The main body of the lgtm command line tool
    :return: Zero if the PR is ready to merge, one if it's not
    """
    options = get_options_parser(args, do_exit=do_exit)
    logging.basicConfig(
        format='%(message)s',
        level=logging.DEBUG if options.verbose else logging.INFO)
    if options.version:
        logger.info(pkg_resources.require('lgtm')[0].version)
        return 0
    log_debug_info(options)
    ready_to_merge = pull_request_ready_to_merge(
        github_token=options.github_token,
        org=options.github_org,
        repo=options.github_repo,
        pr_number=options.github_pr_number,
        owners_file=options.owners_file,
    )
    if ready_to_merge:
        logger.info('Pull request is ready to merge.')
        return 0
    logger.info('Pull Request is NOT ready to merge.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
