from cerberus import Validator

from flash.util import Bson

event_schema = {
    '_id': {
        'type': 'string'
    },
    'circuit_breaker_id': {
        'type': 'string',
        'check_with': Bson.validate_schema_id
    },
    'target': {
        'type': 'string',
        'regex': r'^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$'
    },
    'body': {
        'type': 'dict',
        'default': {}
    },
    'headers': {
        'type': 'dict',
        'default': {}
    }
}

event_validator = Validator(event_schema)
