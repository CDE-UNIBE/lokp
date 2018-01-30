import os

import yaml

from lokp.config.customization import local_profile_directory_path, \
    APPLICATION_YAML


def get_current_profile_extent(request):
    """
    Get the extent from current profile. Get it from YAML, which saves a
    database query
    """

    # Get the path of the yaml
    path = local_profile_directory_path(request)

    if os.path.exists(os.path.join(path, APPLICATION_YAML)):
        profile_stream = open(os.path.join(path, APPLICATION_YAML))
        profile_config = yaml.load(profile_stream)

        if 'application' not in profile_config:
            # Not a valid config file
            return 'null'

        if 'geometry' in profile_config['application']:
            return profile_config['application']['geometry']

    # No local or global file found
    return 'null'
