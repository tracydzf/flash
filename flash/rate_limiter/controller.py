import json
from aiohttp import web
from fastapi import APIRouter
from fastapi import Request

from flash.common.error_code import ERROR_SERVER
from flash.common.resp import resp_error_json, resp_success_json
from flash.models.rate_limiter import RateLimiter
from flash.rate_limiter.schema import rate_limit_entry_validator, rate_limit_rule_validator
from flash.util import DB
from flash.util.validate import Validate

router = APIRouter()


@router.get('/rate_limiter/rule')
async def retrieve_rule(request: Request):
    try:
        # we want to identify the parameter which is used to identify the
        # records
        response = []
        if 'status_code' in request.query_params:
            status_code = request.query_params.get('status_code', 0)
            response = await RateLimiter.get_rule_by_status_code(status_code, DB.get_redis(request))
        elif 'service_id' in request.query_params:
            service_id = request.query_params.get('service_id')
            response = await RateLimiter.get_rule_by_service_id(service_id, DB.get_redis(request))
        elif 'id' in request.query_params:
            _id = request.query_params.get('id')
            Validate.validate_object_id(_id)
            rule = await RateLimiter.get_rule_by_id(_id, DB.get_redis(request))
            if rule:
                response.append(rule)
        else:
            # fallback to get all if no param passed
            response = await RateLimiter.get_all_rules(DB.get_redis(request))
        return resp_success_json(data=response)
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.post('/rate_limiter/rule')
async def create_rule(request: Request):
    try:
        ctx = json.loads(await request.json())
        Validate.validate_schema(ctx, rate_limit_rule_validator)
        await RateLimiter.create_rule(ctx, DB.get_redis(request))
        return resp_success_json(msg='Created rate limiter rule')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.patch('/rate_limiter/rule')
async def update_rule(request: Request):
    try:
        ctx = json.loads(await request.json())
        _id = request.query_params.get('id')
        Validate.validate_schema(ctx, rate_limit_rule_validator)
        Validate.validate_object_id(_id)
        await RateLimiter.update_rule(_id, ctx, DB.get_redis(request))
        return resp_success_json(msg='rate limiter rule updated')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.delete('/rate_limiter/rule')
async def delete_rule(request: Request):
    try:
        # id to delete is from query params
        _id = request.query_params.get('id')
        Validate.validate_object_id(_id)
        await RateLimiter.delete_rule(_id, DB.get_redis(request))
        return resp_success_json(msg='rate limiter rule deleted')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.get('/rate_limiter/entry')
async def retrieve_entry(request: Request):
    try:
        response = []
        if 'rule_id' in request.query_params:
            rule_id = request.query_params.get('rule_id')
            Validate.validate_object_id(rule_id)
            response = await RateLimiter.get_entry_by_rule_id(rule_id, DB.get_redis(request))
        elif 'host' in request.query_params:
            host = request.query_params.get('host')
            response = await RateLimiter.get_entry_by_host(host, DB.get_redis(request))
        elif 'id' in request.query_params:
            _id = request.query_params.get('id')
            Validate.validate_object_id(_id)
            response = await RateLimiter.get_entry_by_id(_id, DB.get_redis(request))
        else:
            response = await RateLimiter.get_all_entries(DB.get_redis(request))
        return resp_success_json(data=response)
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.post('/rate_limiter/entry')
async def create_entry(request: Request):
    try:
        ctx = json.loads(await request.json())
        Validate.validate_schema(ctx, rate_limit_entry_validator)
        await RateLimiter.create_entry(ctx, DB.get_redis(request))
        return resp_success_json(msg='Created rate limiter entry')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.patch('/rate_limiter/entry')
async def update_entry(request: Request):
    try:
        ctx = json.loads(await request.json())
        _id = request.query_params.get('id')
        Validate.validate_schema(ctx, rate_limit_entry_validator)
        Validate.validate_object_id(_id)
        await RateLimiter.update_entry(_id, ctx, DB.get_redis(request))
        return resp_success_json(msg='rate limiter entry updated')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.delete('/rate_limiter/entry')
async def delete_entry(request: Request):
    try:
        # id to delete is from query params
        _id = request.query_params.get('id')
        Validate.validate_object_id(_id)
        await RateLimiter.delete_entry(_id, DB.get_redis(request))
        return resp_success_json(msg='rate limiter entry deleted')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))
