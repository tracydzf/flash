import pydash
from aiohttp import web
from aioredis import Redis
from motor.motor_asyncio import AsyncIOMotorCollection


class DB:
    @staticmethod
    def get(request: web.Request, collection: str) -> AsyncIOMotorCollection:
        """
        gets a mongo collection instance

        @param request: (Request) aiohttp request instance
        @param collection: (str) name of collection to get
        """
        return request.app['mongo'][collection]

    @staticmethod
    def get_redis(request: web.Request) -> Redis:
        """
        gets redis instance

        @param request: (Request) aiohttp request instance
        """
        return request.app['redis']

    @staticmethod
    def format_document(document: object) -> object:
        """
        formats mongo document

        @param document: (object) document to format
        """
        formatted = pydash.omit(document, '_id')
        formatted['_id'] = document['_id']['$oid']
        return formatted

    @staticmethod
    def format_documents(documents: list) -> list:
        """
        formats multiple documents

        @param documents: (list) documents to format
        """
        return list(
            map(lambda document: DB.format_document(document), documents))

    @staticmethod
    async def fetch_members(key: str, db: Redis) -> list:
        """
        gets a set from redis

        @param key: (str) id of set to get
        @param db: (Redis) redis instance
        """
        return await db.smembers(key, encoding='utf-8')
