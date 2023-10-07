import bson
import pydash
from enum import Enum
from motor.motor_asyncio import AsyncIOMotorCollection
from flash.service.schema import service_schema, service_validator

collection_name = 'service'


class ServiceState(Enum):
    DOWN = 'DOWN'
    UP = 'UP'
    OFF = 'OFF'


class Service:
    @staticmethod
    async def create(ctx: object, db: AsyncIOMotorCollection):
        """
        creates a service

        @param ctx: (dict) context of service to create
        @param db: mongo collection instance
        """
        await db.insert_one(ctx)

    @staticmethod
    async def update(_id: str, ctx: object, db: AsyncIOMotorCollection):
        """
        updates a service

        @param id: (str) id of service to update
        @param ctx: (dict) context of fields to update
        @param db: mongo collection instance
        """
        await db.update_one({'_id': bson.ObjectId(_id)}, {'$set': ctx})

    @staticmethod
    async def get_by_id(_id: str, db: AsyncIOMotorCollection) -> object:
        """
        gets a service by id

        @param id: (str) id of service to get
        @param db: mongo collection instance
        """
        return await db.find_one({'_id': bson.ObjectId(_id)})

    @staticmethod
    async def get_by_state(state: str, db: AsyncIOMotorCollection) -> list:
        """
        gets a servie by state

        @param state: (str) state to get service by
        @param db: mongo collection instance
        """
        res = db.find({'state': state})
        return await res.to_list(100)

    @staticmethod
    async def get_by_secure(secure: bool, db: AsyncIOMotorCollection) -> list:
        """
        gets a service by secure

        @param secure: (bool) id of secure to get
        @param db: mongo collection instance
        """
        res = db.find({'secure': secure})
        return await res.to_list(100)

    @staticmethod
    async def get_by_path(path: str, db: AsyncIOMotorCollection) -> list:
        """
        gets service by path

        @param path: (str) path of service
        @param db: mongo connection
        """
        res = db.find({'path': path})
        return await res.to_list(100)

    @staticmethod
    async def get_all(db: AsyncIOMotorCollection) -> list:
        """
        gets all services

        @param db: mongo collection instance
        """
        res = db.find({})
        return await res.to_list(100)

    @staticmethod
    async def remove(_id: str, db: AsyncIOMotorCollection):
        """
        removes a service

        @param id: (str) id of service to remove
        @param db: mongo collection instance
        """
        await db.delete_one({'_id': bson.ObjectId(_id)})

    @staticmethod
    async def add_target(_id: str, target: str, db: AsyncIOMotorCollection):
        """
        adds a target to a service

        @param id: (str) id of service
        @param target: (str) target to add to service
        @param db: mongo collection instance
        """
        await db.update_one({'_id': bson.ObjectId(_id)}, {'$push': {'targets': target}})

    @staticmethod
    async def remove_target(_id: str, target: str, db: AsyncIOMotorCollection):
        """
        removes a target from a service

        @param id: (str) id of service
        @param target: (str) target to remove from service
        @param db: mongo collection instance
        """
        await db.update_one({'_id': bson.ObjectId(_id)}, {'$pull': {'targets': target}})

    @staticmethod
    async def advance_target(_id: str, db: AsyncIOMotorCollection):
        """
        advances target to next in list

        @param id: (str) id of service
        @param db: mongo collection instance
        """
        ctx = {}
        service = await Service.get_by_id(_id, db)
        if 'targets' in service and len(service['targets']) > 0:
            next_target_index = service['cur_target_index'] + 1
            if next_target_index <= len(service['targets']) - 1:
                ctx['cur_target_index'] = next_target_index
            else:
                ctx['cur_target_index'] = 0
            await Service.update(_id, ctx, db)

    @staticmethod
    async def add_whitelist(_id: str, host: str, db: AsyncIOMotorCollection):
        """
        adds a whitelisted host to a service

        @param id: (str) id of service
        @param host: (str) host to add to service
        @param db: mongo collection instance
        """
        await db.update_one({'_id': bson.ObjectId(_id)}, {'$push': {'whitelisted_hosts': host}})

    @staticmethod
    async def remove_whitelist(_id: str, host: str, db: AsyncIOMotorCollection):

        """
        removes a whitelisted host from a service

        @param id: (str) id of service
        @param host: (str) host to remove from service
        @param db: mongo collection instance
        """
        await db.update_one({'_id': bson.ObjectId(_id)}, {'$pull': {'whitelisted_hosts': host}})

    @staticmethod
    async def add_blacklist(_id: str, host: str, db: AsyncIOMotorCollection):
        """
        adds a blacklisted host to a service

        @param id: (str) id of service
        @param host: (str) host to add to service
        @param db: mongo collection instance
        """

        await db.update_one({'_id': bson.ObjectId(_id)}, {'$push': {'blacklisted_hosts': host}})

    @staticmethod
    async def remove_blacklist(_id: str, host: str, db: AsyncIOMotorCollection):
        """
        removes a blacklisted host from a service

        @param id: (str) id of service
        @param host: (str) host to remove from service
        @param db: mongo collection instance
        """
        await db.update_one({'_id': bson.ObjectId(_id)}, {'$pull': {'blacklisted_hosts': host}})

    @staticmethod
    async def check_exists(_id, db: AsyncIOMotorCollection):
        """
        checks if a service exists

        @param id: (str) id of service
        @param db: mongo collection instance
        """
        service = await Service.get_by_id(_id, db)
        if service is None:
            raise Exception({
                'message': 'Service id provided does not exist',
                'status_code': 400
            })
