from cerberus import Validator

from flash.util import Bson

rate_limit_rule_schema = {
    '_id': {
        'type': 'string',
    },
    'max_requests': {
        'type': 'integer',
        'min': 0
    },
    'service_id': {
        'type': 'string',
        'check_with': Bson.validate_schema_id
    },
    'timeout': {
        'type': 'integer',
        'min': 0
    },
    'message': {
        'type': 'string',
    },
    'status_code': {
        'type': 'integer',
    }
}

rate_limit_entry_schema = {
    '_id': {
        'type': 'string'
    },
    'rule_id': {
        'type': 'string',
        'check_with': Bson.validate_schema_id
    },
    'host': {
        'type': 'string',
        'regex': r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    },
    'count': {
        'type': 'integer',
        'min': 0
    }
}

rate_limit_rule_validator = Validator(rate_limit_rule_schema)
rate_limit_entry_validator = Validator(rate_limit_entry_schema)
