from pyramid.view import view_config
from lmkp.config import profile_directory_path
import os
import glob
import yaml

@view_config(route_name='profile_store', renderer='json')
def profile_store(request):
    """
    Return a JSON representation (can be used to build an Ext Store) of all
    available profiles.
    In order to appear in this list, a profile needs to be a valid YAML (.yml)
    file located in /profiles and it must contain an attribute "name".
    """
    
    data = []
    
    profile_dir = profile_directory_path(request)

    for file in glob.glob(os.path.join(profile_dir, '*.yml')):
        try:
            curr_file = open(file, 'r')
            curr_yaml = yaml.load(curr_file)
            
            try:
                name = curr_yaml["application"]["name"]
                profile = os.path.splitext(os.path.basename(file))[0]
                data.append({
                    'name': name,
                    'profile': profile
                })
            
            except TypeError:
                # Profile is empty.
                pass
            
            except KeyError:
                # No attribute "name".
                pass
                
        except IOError:
            # No profile found.
            pass
    
    ret = {}
    ret['data'] = data
    ret['success'] = True
    ret['total'] = len(data)

    return ret