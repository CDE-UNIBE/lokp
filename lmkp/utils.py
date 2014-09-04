def validate_item_type(item_type):
    if item_type in ['a', 'activity', 'activities']:
        return 'a'
    elif item_type in ['sh', 'stakeholder', 'stakeholders']:
        return 'sh'
    else:
        raise Exception('"%s" is not a valid item type!' % item_type)
