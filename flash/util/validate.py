import bson
import re
from cerberus import Validator


class Validate:
    @staticmethod
    def validate_object_id(id: str):
        """
        validates a bson object id

        @param id: (str) id to be validated
        """
        if not bson.ObjectId.is_valid(id):
            raise Exception({
                'message': 'Invalid id provided',
                'status_code': 400
            })

    @staticmethod
    def validate_schema(schema: object, validator: Validator):
        """
        validates a given object with given validator

        @param ctx: (object) object to be validated
        @param validator: (Validator) validator to validate schema with
        """
        if not validator.validate(schema):
            raise Exception({
                'message': 'Invalid data provided',
                'status_code': 400,
                'errors': validator.errors
            })

    @staticmethod
    def validate_regex_field(field, regex, error):
        try:
            re.compile(regex)
        except re.error as err:
            error(field, 'Must be a valid regex')
