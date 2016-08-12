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

from lgtm import integrations
from lgtm import pull_request_ready_to_merge


logger = logging.getLogger(__name__)


def get_options_parser(args=None, do_exit=True):
    """
    Parses and validates sys.argv + environment variables into an options object
    :return: the options object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--github-token',
                        help='GitHub API Token, can also use GITHUB_TOKEN environment variable',
                        default=os.environ.get('GITHUB_TOKEN'))
    parser.add_argument('--github-org', help='GitHub organization name')
    parser.add_argument('--github-repo', help='Pull request repository name')
    parser.add_argument('--github-pr-number', help='Pull request number')
    parser.add_argument('--owners-file', help='Relative path to OWNERS file', default='OWNERS')
    parser.add_argument('--skip-approval',
                        action='append',
                        default=[],
                        dest='skip_approval_branches',
                        help='No requirement to approve merges into this branch')
    parser.add_argument('--skip-assignment',
                        action='store_true',
                        help='Do not assign the PR to anyone on the review list')
    parser.add_argument('--skip-notification',
                        action='append',
                        default=[],
                        dest='skip_notification_branches',
                        help='Do not send notifications for PRs to this branch')
    parser.add_argument('--integration',
                        help='Extract org/repo/pr from environment variables specific to a platform',
                        choices=['jenkins', 'travis'],
                        default=None)
    parser.add_argument('--version', help='Print version and exit', action='store_true')
    parser.add_argument('--verbose',
                        help='Print commands that are running and other debug info',
                        action='store_true')
    options = parser.parse_args(args)
    logging.basicConfig(format='%(message)s')
    logger.setLevel(logging.DEBUG if options.verbose else logging.INFO)
    if options.integration:
        defaults = integrations.get_options_defaults_dict(options.integration)
        for option, value in defaults.items():
            setattr(options, option, value)
        logger.debug('Options: %r' % options)
    if options.version:
        return options
    required = ['github_token', 'github_org', 'github_repo', 'github_pr_number']
    if not all([getattr(options, option) for option in required]):
        parser.print_usage()
        if do_exit:
            exit()
    options.github_pr_number = int(options.github_pr_number)
    return options


def main(args=None, do_exit=True):
    """
    The main body of the lgtm command line tool
    :return: Zero if the PR is ready to merge, one if it's not
    """
    options = get_options_parser(args, do_exit=do_exit)
    if options.version:
        logger.info(pkg_resources.require('lgtm')[0].version)
        return 0
    ready_to_merge = pull_request_ready_to_merge(
        github_token=options.github_token,
        org=options.github_org,
        repo=options.github_repo,
        pr_number=options.github_pr_number,
        owners_file=options.owners_file,
        options={'skip_approval_branches': options.skip_approval_branches,
                 'skip_assignment': options.skip_assignment,
                 'skip_notification_branches': options.skip_notification_branches,
                 }
    )
    if ready_to_merge:
        logger.info('Pull request is ready to merge.')
        return 0
    logger.info('Pull Request is NOT ready to merge.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
