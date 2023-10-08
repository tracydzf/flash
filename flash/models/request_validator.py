from motor.motor_asyncio import AsyncIOMotorCollection
from cerberus import Validator
import bson

from flash.models.service import Service
from password_strength import PasswordPolicy, PasswordStats


class RequestValidator:
    @staticmethod
    async def create(ctx: object, request_validator_db: AsyncIOMotorCollection, service_db: AsyncIOMotorCollection):
        """
        Creates a request validation entry.

        @param document: (object) document to be inserted
        @param db: (object) db connection
        """
        try:
            if 'schema' in ctx:
                Validator(ctx['schema'])
            if 'service_id' in ctx:
                await Service.check_exists(ctx['service_id'], service_db)
            await request_validator_db.insert_one(ctx)
        except Exception as err:
            raise Exception({
                'message': 'error in provided schema',
                'context': err.args[0],
                'status_code': 400
            })

    @staticmethod
    async def update(request_validator_id: str, ctx: object, db: AsyncIOMotorCollection):
        """
        Updates a request validation entry.

        @param id: (string) the ID of the request validation entry to update
        @param document: (object) the data to be inserted into this request validation entry
        @param db: (object) db connection
        """

        await db.update_one({'_id': bson.ObjectId(request_validator_id)}, {'$set': ctx})

    @staticmethod
    async def delete(_id: str, db: AsyncIOMotorCollection):
        """
        Deletes a request validation entry.

        @param id_: (string) the ID of the request validation entry to delete
        @param db: (object) db connection
        @return: true for success, false for failure (expand on this after discussion)
        """
        await db.delete_one({'_id': bson.ObjectId(_id)})

    @staticmethod
    async def get_all(db: AsyncIOMotorCollection):
        """
        Gets all request validation entries

        @param db: (object) db connection
        @return: the documents with the provided serviceId
        """
        res = db.find({})
        return await res.to_list(100)

    @staticmethod
    async def get_by_id(_id: str, db: AsyncIOMotorCollection):
        return await db.find_one({'_id': bson.ObjectId(_id)})

    @staticmethod
    async def get_by_service_id(service_id: str, db: AsyncIOMotorCollection):
        """
        Gets a request validation entry by the service_id provided

        @param service_id: (string) ID for the service which the request is (coming from? targeting?)
        @param db: (object) db connection
        @return: the documents with the provided serviceId
        """
        res = db.find({"service_id": service_id})
        return await res.to_list(100)

    @staticmethod
    async def get_by_method(method: str, db: AsyncIOMotorCollection):
        """
        Gets a request validation entry by the method provided

        @param method: (string) HTTP method that the request is transmitted by
        @param db: (object) db connection
        @return: the documents using the provided method
        """
        res = db.find({"method": method})
        return await res.to_list(100)

    @staticmethod
    async def validate_schema(ctx: object, schema: object):
        """
        Validates that the request body provided matches the schema for the request.

        @param ctx: (object) context to validate
        @param schema
        """
        request_validator = Validator(schema)
        if not request_validator.validate(ctx):
            raise Exception({
                'message': 'Body provided does not match provided schema',
                'status_code': 400
            })

    @staticmethod
    async def enforce_policy(password: str, policy: object):
        """
        validates that the given password matches the provided password policy.

        @param password: (string) password to be validated
        @param policy: (object) password requirements
        """
        ctx = {}
        kwargs_mapping = {
            'length': 'length',
            'upper_case_count': 'uppercase',
            'numbers_count': 'numbers',
            'specials_count': 'special',
            'non_letters_count': 'nonletters',
        }

        for key in kwargs_mapping.keys():
            if key in policy:
                ctx[kwargs_mapping[key]] = policy[key]

        password_policy = PasswordPolicy.from_names(**ctx)
        res = password_policy.test(password)
        if res != []:
            raise Exception({
                'message': 'Password provided does not match policy configured',
                'status_code': 400
            })

    @staticmethod
    async def enforce_strength(password: str, strength_percentage: float):
        """
        enforces password to have specified strength percentage

        @param password: (str) to enforce strength
        @param strength: (float) cut off strength percentage
        """
        stats = PasswordStats(password)
        if stats.strength() < strength_percentage:
            raise Exception({
                'message': 'Password strength not up to standard',
                'status_code': 400
            })
