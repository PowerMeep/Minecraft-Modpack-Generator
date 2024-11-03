import logging
logger = logging.getLogger()


def get_item(element,
             element_type: str,
             store: dict):
    if type(element) is list:
        temp = []
        for el in element:
            mods = get_item(
                element=el,
                element_type=element_type,
                store=store
            )
            temp.append(mods)
        return temp
    elif element is not None:
        out = store.get(element)
        if out is None:
            logger.error(f'Could not find {element_type}: {element}')
        return out
    else:
        return None


def get_layers(element):
    from models.layer import layers_by_name
    return get_item(
        element=element,
        element_type='layer',
        store=layers_by_name
    )


def load_items(path: str,
               callback):
    logger.warning(f'Reading from file: {path}')
    import json
    with open(path) as f:
        raw = f.read()
        all_mods = json.loads(raw)
        for m_dict in all_mods:
            callback(m_dict)


def load_named_items(path: str,
                     callback):
    logger.warning(f'Reading from file: {path}')
    import json
    with open(path) as f:
        raw = f.read()
        all_mods = json.loads(raw)
        for m_dict in all_mods:
            if 'name' not in m_dict:
                logger.error(f'Skipping unnamed item: {json.dumps(m_dict)}')
            else:
                callback(m_dict)


def validate_type(name: str,
                  types_by_field: dict,
                  data: dict) -> list:
    out = []
    for field, expected in types_by_field.items():
        expected_type = expected[0]
        required = expected[1]
        value = data.get(field)
        if value is None and not required:
            continue
        if type(value) is not expected_type:
            logger.error(f'{name}: {field} is not of type {expected_type}')
    return out
