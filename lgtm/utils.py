from collections import OrderedDict

# prefix to the notification comment, also used to identify the comment during future runs
DEFAULT_REVIEW_COMMENT_PREFIX = 'This pull request requires a code review.'


def ordered_set(item_list):
    """
    Return a list of the unique set of items, with order maintained by first appearance
    :param item_list: A list of items that can be compared to each other
    :return: a list of unique items
    """
    # useful b/c Python does not have an ordered set builtin
    items = OrderedDict()
    for item in item_list:
        items[item] = item
    return items.values()


def make_mention_string(logins):
    return ' '.join(['@%s' % login for login in sorted(logins)])


def generate_comment(author, reviewers, required, prefix=None, approval_required=True):
    if not reviewers and not required:
        return None
    prefix = prefix or DEFAULT_REVIEW_COMMENT_PREFIX
    message = '%s\n\n' % prefix

    reviewers = set(reviewers) - set([author])
    required = set(required) - set([author])
    left_overs = set(reviewers) - set(required)

    if not approval_required:
        message += 'No approval necessary on this PR.\n'
        message += '/cc '
        message += make_mention_string(reviewers)
    else:
        if required:
            message += 'All of the following reviewers must sign off: '
            message += make_mention_string(required)
            if left_overs:
                message += '\n\n'
                message += 'Optional: %s' % make_mention_string(left_overs)
        else:
            message += 'One of the following reviewers must sign off: '
            message += make_mention_string(reviewers)
    message = message.strip()
    return message
