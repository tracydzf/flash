import bson
import pydash
from enum import Enum
from aioredis import Redis as AioRedis
from motor.motor_asyncio import AsyncIOMotorCollection

from flash.models.service import Service


class CircuitBreakerStatus(Enum):
    ON = 'ON'
    OFF = 'OFF'


class CircuitBreaker:
    @staticmethod
    async def create(ctx: object, circuit_breaker_db: AsyncIOMotorCollection, service_db: AsyncIOMotorCollection):
        """
        creates a circuit breaker

        @param ctx: (object) context to create
        @param circuit_breaker_db: mongo instance
        @param service_db: mongo instance
        """
        if 'service_id' in ctx:
            await Service.check_exists(ctx['service_id'], service_db)
        await circuit_breaker_db.insert_one(ctx)

    @staticmethod
    async def update(_id: str, ctx: object, db: AsyncIOMotorCollection):
        """
        updates circuit breaker

        @param id: (str) id of circuit breaker
        @param ctx: (object) context of update
        @param db: mongo instance
        """
        await db.update_one({'_id': bson.ObjectId(_id)}, {'$set': ctx})

    @staticmethod
    async def get_by_id(_id: str, db: AsyncIOMotorCollection):
        """
        gets cirbuit breaker by id

        @param id: (str) id of cirbuit breaker
        @param db: mongo instance
        """
        return await db.find_one({'_id': bson.ObjectId(_id)})

    @staticmethod
    async def get_by_service_id(service_id: str, db: AsyncIOMotorCollection):
        """
        gets cirbuit breaker by service id

        @param service_id: (str) service id of cirbuit breaker
        @param db: mongo instance
        """
        res = db.find({'service_id': service_id})
        return await res.to_list(100)

    @staticmethod
    async def get_by_status_code(status_code: int, db: AsyncIOMotorCollection):
        """
        gets cirbuit breaker by status code

        @param status_code: (int) status code of cirbuit breaker
        @param db: mongo instance
        """
        res = db.find({'status_code': status_code})
        return await res.to_list(100)

    @staticmethod
    async def get_by_method(method: str, db: AsyncIOMotorCollection):
        """
        gets cirbuit breaker by method

        @param metod: (str) method of cirbuit breaker
        @param db: mongo instance
        """
        res = db.find({'method': method})
        return await res.to_list(100)

    @staticmethod
    async def get_by_threshold(threshold: float, db: AsyncIOMotorCollection):
        """
        gets cirbuit breaker by threshold

        @param threshold: (float) threshold of cirbuit breaker
        @param db: mongo instance
        """
        res = db.find({'threshold': threshold})
        return await res.to_list(100)

    @staticmethod
    async def get_all(db: AsyncIOMotorCollection):
        """
        gets all circuit breakers

        @param db: mongo instance
        """
        res = db.find({})
        return await res.to_list(100)

    @staticmethod
    async def remove(_id: str, db: AsyncIOMotorCollection):
        """
        removes a cirbuit breaker

        @param id: (str) id of circuit breaker
        @param db: mongo instance
        """
        await db.delete_one({'_id': bson.ObjectId(_id)})

    @staticmethod
    async def check_exists(circuit_breaker_id: str, db: AsyncIOMotorCollection):
        """
        checks if circuit breaker exists

        @param circuit_breaker_id: (str) id of circuit breaker
        @param db: mongo instance
        """
        circuit_breaker = await CircuitBreaker.get_by_id(circuit_breaker_id, db)
        if circuit_breaker is None:
            raise Exception({
                'message': 'Circuit breaker id provided does not exist',
                'status_code': 400
            })

    @staticmethod
    async def incr_tripped_count(_id: str, db: AsyncIOMotorCollection):
        """
        increments tripped count

        @param id: (str) id of circuit breaker
        @param db: mongo instance
        """
        await db.update_one({'_id': bson.ObjectId(_id)}, {'$inc': {'tripped_count': 1}})

    @staticmethod
    def count_key(_id):
        """
        returns count key
        """
        return f'{_id}.count'

    @staticmethod
    def queued_key(_id):
        """
        returns queued key
        """
        return f'{_id}.queued'

    @staticmethod
    async def incr_count(_id: str, db: AioRedis):
        """
        increments count

        @param id: (str) id of circuit breaker
        @param db: redis instance
        """
        await db.incr(CircuitBreaker.count_key(_id))

    @staticmethod
    async def get_count(_id: str, db: AioRedis):
        """
        gets count

        @param id: (str) id of circuit breaker
        @param db: redis instance
        """
        return await db.get(CircuitBreaker.count_key(_id))

    @staticmethod
    async def set_count(_id: str, count: int, timeout: int, db: AioRedis):
        """
        sets count

        @param id: (str) id of circuit breaker
        @param count: (int) number to set
        @param timeout: (int) redis expire time
        @param db: redis instance
        """
        await db.set(CircuitBreaker.count_key(_id), count, ex=timeout)

    @staticmethod
    async def set_queued(_id: str, queued: str, timeout: int, db: AioRedis):
        """
        sets queued (if cooldown has been queued)

        @param id: (str) id of circuit breaker
        @param queued: (str) queue to set
        @param timeout: (int) redis expire time
        @param db: redis instance
        """

        await db.set(CircuitBreaker.queued_key(_id), queued, ex=timeout)

    @staticmethod
    async def get_queued(_id: str, db: AioRedis):
        """
        gets queued

        @param id: (str) id of circuit breaker
        @param db: redis instance
        """
        return await db.get(CircuitBreaker.queued_key(_id))
