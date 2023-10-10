from cerberus import Validator
from api.util import Bson

endpoint_cache_schema = {
    '_id': {
        'type': 'string'
    },
    'service_id': {
        'type': 'string',
        'check_with': Bson.validate_schema_id
    },
    'timeout': {
        'type': 'integer',
        'min': 0
    },
    'response_codes': {
        'type': 'list'
    }
}

endpoint_cache_validator = Validator(endpoint_cache_schema)
