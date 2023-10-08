from cerberus import Validator

from flash.util import Bson

circuit_breaker_schema = {
    '_id': {
        'type': 'string'
    },
    'status': {
        'type': 'string',
        'allowed': ['ON', 'OFF'],
        'default': 'ON'
    },
    'service_id': {
        'type': 'string',
        'check_with': Bson.validate_schema_id
    },
    'cooldown': {
        'type': 'integer',
        'default': 60,
        'min': 0
    },
    'status_codes': {
        'type': 'list',
        'schema': {
            'type': 'integer',
        },
        'default': []
    },
    'method': {
        'type': 'string',
        'allowed': ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATH']
    },
    'threshold': {
        'type': 'float',
        'min': 0.0,
        'max': 1.0
    },
    'period': {
        'type': 'integer',
        'min': 0,
        'default': 60
    },
    'tripped_count': {
        'type': 'integer',
        'default': 0
    },
}

circuit_breaker_validator = Validator(circuit_breaker_schema)
