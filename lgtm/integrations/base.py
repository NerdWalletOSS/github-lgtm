import os


def get_options_defaults_dict(integration_type, env=None):
    if env is None:
        env = os.environ
    if integration_type == 'jenkins':
        import jenkins
        return jenkins.get_pull_request_dict(env)
    elif integration_type == 'travis':
        import travis
        return travis.get_pull_request_dict(env)
    else:
        raise NotImplementedError()
