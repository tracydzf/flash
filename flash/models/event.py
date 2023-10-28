import bson
from motor.motor_asyncio import AsyncIOMotorCollection

from flash.models.circuit_breaker import CircuitBreaker
from flash.util import Api

collection_name = 'event'


class Event:
    @staticmethod
    async def create(ctx: object, event_db: AsyncIOMotorCollection, circuit_breaker_db: AsyncIOMotorCollection):
        """
        creates an event

        @param ctx: (dict) event to create
        @param event_db: mongo collection instance
        @param circuit_breaker_db: mongo collection instance
        """
        if 'circuit_breaker_id' in ctx:
            await CircuitBreaker.check_exists(ctx['circuit_breaker_id'], circuit_breaker_db)
        await event_db.insert_one(ctx)

    @staticmethod
    async def update(_id: str, ctx: object, db: AsyncIOMotorCollection):
        """
        updates an event

        @param id: (str) id of event
        @param ctx: (dict) fields to update
        @param db: mongo collection instance
        """
        await db.update_one({'_id': bson.ObjectId(_id)}, {'$set': ctx})

    @staticmethod
    async def get_by_id(_id: str, db: AsyncIOMotorCollection):
        """
        gets event by id

        @param id: (str) id to get event by
        @param db: mongo collection instance
        """
        return await db.find_one({'_id': bson.ObjectId(_id)})

    @staticmethod
    async def get_by_circuit_breaker_id(_id: str, db: AsyncIOMotorCollection):
        """
        gets event by circuit breaker id

        @param id: (str) circuit breaker id to get event by
        @param db: mongo collection instance
        """
        res = db.find({'circuit_breaker_id': _id})
        return await res.to_list(100)

    @staticmethod
    async def get_by_target(target: str, db: AsyncIOMotorCollection):
        """
        gets event by target

        @param target: (str) target to get event by
        @param db: mongo collection instance
        """
        res = db.find({'target': target})
        return await res.to_list(100)

    @staticmethod
    async def get_all(db: AsyncIOMotorCollection):
        """
        gets all events

        @param db: mongo collection instance
        """
        res = db.find({})
        return await res.to_list(100)

    @staticmethod
    async def remove(_id: str, db: AsyncIOMotorCollection):
        """
        removes event

        @param id: (str) id of event
        @param db: mongo collection instance

        """
        await db.delete_one({'_id': bson.ObjectId(_id)})

    @staticmethod
    async def handle_event(ctx: object):
        """
        handles event

        @param ctx: (dict) body of event to handle
        """
        res = await Api.call(method='post', url=ctx['target'], data=ctx['body'], headers=ctx['headers'])
        # TODO send email to admins on failure
