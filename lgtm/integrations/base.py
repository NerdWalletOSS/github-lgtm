def get_options_defaults_dict(integration_type):
    if integration_type == 'jenkins':
        import jenkins
        return jenkins.get_pull_request_dict()
    else:
        raise NotImplementedError()
