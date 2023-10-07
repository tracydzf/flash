import json
import bson
from bson import json_util


class Bson:
    @staticmethod
    def to_json(ctx: object):
        """
        converts bson object to json
        """
        return json.loads(json_util.dumps(ctx))

    @staticmethod
    def validate_schema_id(field, value, error):
        """
        validates schema object id
        """
        if not bson.ObjectId.is_valid(value):
            error(field, 'Must be a bson object id')
