import bson
from cerberus import Validator

from flash.util import Bson

request_validator_schema = {
    '_id': {
        'type': 'string'
    },
    'service_id': {
        'type': 'string',
        'check_with': Bson.validate_schema_id
    },
    'method': {
        'type': 'string',
        'allowed': ['POST', 'PUT']
    },
    'schema': {
        'type': 'dict'
    },
    'password_field': {
        'type': 'string'
    },
    'password_policy': {
        'type': 'dict',
        'schema': {
            'length': {
                'type': 'integer',
                'min': 0
            },
            'upper_case_count': {
                'type': 'integer',
                'min': 0
            },
            'numbers_count': {
                'type': 'integer',
                'min': 0
            },
            'specials_count': {
                'type': 'integer',
                'min': 0
            },
            'non_letters_count': {
                'type': 'integer',
                'min': 0
            },
            'strength': {
                'type': 'float',
                'min': 0.0,
                'max': 1.0
            }
        }
    },
    'err_response_code': {
        'type': 'integer',
    }
}

request_validator = Validator(request_validator_schema)
