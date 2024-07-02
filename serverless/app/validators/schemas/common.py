from app.validators import NormalizerUtils

ulid_schema = {
    'type': 'string',
    'coerce': (str, NormalizerUtils.trim),
    'required': True,
    'empty': False,
    'valid_ulid': True,
}

user_id_schema = {
    'type': 'string',
    'coerce': (str, NormalizerUtils.trim),
    'required': True,
    'empty': False,
    'regex': r'^[a-zA-Z0-9\-_]{28,32}$',
}

slug_schema = {
    'type': 'string',
    'coerce': (str, NormalizerUtils.trim),
    'required': True,
    'empty': False,
    'maxlength': 128,
    'regex': r'^[0-9a-z\-]+$',
}

random_slug_schema = {
    'type': 'string',
    'coerce': (str, NormalizerUtils.trim),
    'required': True,
    'empty': False,
    'maxlength': 128,
    'regex': r'^[0-9a-zA-Z_\-]+$',
}

get_list_schemas = {
    'count': {
        'type': 'integer',
        'coerce': int,
        'required': False,
        'min': 1,
        'max': 50,
        'default': 10,
    },
    'order': {
        'type': 'string',
        'required': False,
        'allowed': ['asc', 'desc'],
        'default': 'asc',
    },
}

schema_with_detail = {
    'type': 'boolean',
    'coerce': (str, NormalizerUtils.to_bool),
    'required': False,
    'empty': True,
    'default': False,
}
