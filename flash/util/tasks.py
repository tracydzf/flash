
import asyncio
import aioredis
import pydash
from celery import Celery, Task
from celery.schedules import crontab
from flash.util.env import REDIS, DB
from motor.motor_asyncio import AsyncIOMotorClient

from flash.models.circuit_breaker import CircuitBreaker
from flash.models.endpoint_cacher import EndpointCacher
from flash.models.event import Event
from flash.models.insights import Insights
from flash.models.rate_limiter import RateLimiter
from flash.models.service import Service
from flash.util import Api

tasks = Celery('api.util.tasks', broker=REDIS, backend=REDIS)

tasks.conf.beat_schedule = {
    'raven.api.rate_limiter.clear_empty_entries': {
        'task': 'raven.api.task.async',
        'schedule': crontab(),
        'args': [{
            'func': 'RateLimiter.clear_empty_entries',
            'args': ['redis'],
            'kwargs': {}
        }]
    }
}


def arg_needs_resource(arg: str, resource: str) -> bool:
    """
    checks if an arg needs a mongo instance
    """
    return pydash.is_string(arg) and resource in arg


def get_mongo_collection(arg: str) -> str:
    """
    parses and returns a mongo collection from an arg
    """
    return arg.split(':')[1]


def is_supported_func(func: str, funcs: dict) -> bool:
    return func in funcs


def map_args_to_resources(args: list, resources: dict) -> list:
    """
    maps args to resources singleton instances
    """
    mapped_args = []

    for index, arg in enumerate(args):
        if arg_needs_resource(arg, 'mongo'):
            collection = get_mongo_collection(arg)
            mapped_args.append(resources['mongo'][collection])
        elif arg_needs_resource(arg, 'redis'):
            mapped_args.append(resources['redis'])
        else:
            mapped_args.append(arg)

    return mapped_args


class TaskProvider(Task):
    _mongo_instance = None
    _redis_instance = None
    _event_loop = None
    _supported_funcs = {
        'Api.call': Api.call,
        'CircuitBreaker.incr_count': CircuitBreaker.incr_count,
        'CircuitBreaker.incr_tripped_count': CircuitBreaker.incr_tripped_count,
        'CircuitBreaker.set_queued': CircuitBreaker.set_queued,
        'CircuitBreaker.update': CircuitBreaker.update,
        'EndpointCacher.set_cache': EndpointCacher.set_cache,
        'Event.handle_event': Event.handle_event,
        'Insights.create': Insights.create,
        'RateLimiter.clear_empty_entries': RateLimiter.clear_empty_entries,
        'RateLimiter.create_entry': RateLimiter.create_entry,
        'RateLimiter.increment_entry_count': RateLimiter.increment_entry_count,
        'RateLimiter.update_entry': RateLimiter.update_entry,
        'Service.advance_target': Service.advance_target,
        'Service.update': Service.update
    }

    @property
    def mongo(self):
        if self._mongo_instance is None:
            self._mongo_instance = AsyncIOMotorClient(DB).raven
        return self._mongo_instance

    @property
    def redis(self):
        if self._redis_instance is None:
            self._redis_instance = self.loop.run_until_complete(
                aioredis.from_url(REDIS)
            )
        return self._redis_instance

    @property
    def loop(self):
        if self._event_loop is None:
            self._event_loop = asyncio.get_event_loop()
        return self._event_loop


@tasks.task(base=TaskProvider, name='gateway.api.task.async')
def queue_async_func(params: dict):
    """
    handles async task

    supports ability to pass mongo and redis as params
    mongo: "mongo:collection_name"
    redis: "redis"
    """
    resources = {
        'mongo': queue_async_func.mongo,
        'redis': queue_async_func.redis
    }

    if is_supported_func(params['func'], queue_async_func._supported_funcs):
        mapped_args = map_args_to_resources(params['args'], resources)
        return queue_async_func.loop.run_until_complete(
            queue_async_func._supported_funcs[params['func']](*mapped_args, **params['kwargs']))


@tasks.task(base=TaskProvider, name='gateway.api.task.sync')
def queue_sync_func(params):
    """
    handles sync task
    """
    if is_supported_func(params['func'], queue_sync_func._supported_funcs):
        return queue_sync_func._supported_funcs[params['func']](
            *params['args'], **params['kwargs'])
