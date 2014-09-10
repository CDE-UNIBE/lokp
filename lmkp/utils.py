"""
:mod:`lmkp.utils` provides some useful helper functions.
"""


def validate_bbox(bbox):
    """
    Tests if a string is a valid bounding box. It is assumed valid if
    the string contains 4 comma-separated numbers. If valid, the
    bounding box is returned as list.

    Args:
        bbox (str): A string containing the bounding box.

    Returns:
        list or None. If valid, a list with 4 float numbers is returned.
        If not valid, None is returned.
    """
    try:
        bbox_parts = bbox.split(',')
        if len(bbox_parts) != 4:
            return None
        return map(float, bbox_parts)
    except:
        return None


def validate_item_type(item_type):
    """
    Tests if a string is a valid item type for either Activities or
    Stakeholders. Returns a standardized short representation of it if
    valid.

    Args:
        item_type (str): A string with an item type.

    Returns:
        str. A short representation of the item type.

    Raises:
        Exception
    """
    if item_type in ['a', 'activity', 'activities']:
        return 'a'
    elif item_type in ['sh', 'stakeholder', 'stakeholders']:
        return 'sh'
    else:
        raise Exception('"%s" is not a valid item type!' % item_type)
