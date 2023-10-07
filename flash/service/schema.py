from cerberus import Validator

from flash.util.validate import Validate

service_schema = {
    '_id': {
        'type': 'string'
    },
    'path': {
        'type': 'string',
        'check_with': Validate.validate_regex_field
    },
    'state': {
        'type': 'string',
        'allowed': ['BROKEN', 'DOWN', 'UP', 'OFF'],
        'default': 'OFF'
    },
    'secure': {
        'type': 'boolean',
        'default': False
    },
    'targets': {
        'type': 'list',
        'schema': {
            'type': 'string',
            'regex': r'^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$'
        },
        'empty': False,
    },
    'cur_target_index': {
        'type': 'integer',
        'default': 0,
    },
    'whitelisted_hosts': {
        'type': 'list',
        'schema': {
            'type': 'string',
            'regex': r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        },
        'default': []
    },
    'blacklisted_hosts': {
        'type': 'list',
        'schema': {
            'type': 'string',
            'regex': r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        },
        'default': []
    },
    'public_key': {
        'type': 'string'
    }
}

service_validator = Validator(service_schema)
