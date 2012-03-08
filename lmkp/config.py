# To change this template, choose Tools | Templates
# and open the template in the editor.

import os.path

def config_file_path():
    """
    Returns the absolute path to the config.yaml file
    """
    return "%s/config.yaml" % os.path.dirname(__file__)