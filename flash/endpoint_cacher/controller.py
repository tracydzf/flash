import json

import pydash
from fastapi import APIRouter
from fastapi import Request
from flash.common.error_code import ERROR_SERVER, ERROR_PARAMETER_ERROR
from flash.common.resp import resp_error_json, resp_success_json
from flash.endpoint_cacher.schema import endpoint_cache_validator
from flash.models.endpoint_cacher import EndpointCacher
from flash.util import DB, Bson
from flash.util.validate import Validate
from flash.service import controller as service_controller

router = APIRouter()


@router.get('/endpoint_cache')
async def get_handler(request: Request):
    try:
        response = []
        if 'id' in request.query_params:
            _id = request.query_params.get('id')
            Validate.validate_object_id(_id)
            cache = await EndpointCacher.get_by_id(_id, DB.get_redis(request))
            if not pydash.is_empty(cache):
                response.append(cache)
        elif 'service_id' in request.query_params:
            service_id = request.query_params.get('service_id')
            Validate.validate_object_id(service_id)
            response = await EndpointCacher.get_by_service_id(service_id, DB.get_redis(request))
        else:
            response = await EndpointCacher.get_all(DB.get_redis(request))

        return resp_success_json(data=response)
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.patch('/endpoint_cache')
async def patch_handler(request: Request):
    try:
        ctx = json.loads(await request.json())
        _id = request.query_params.get('id')
        Validate.validate_schema(ctx, endpoint_cache_validator)
        Validate.validate_object_id(_id)
        await EndpointCacher.update(_id, pydash.omit(ctx, 'service_id', 'response_codes'), DB.get_redis(request))

        return resp_success_json(msg='Endpoint cache updated')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.patch('/endpoint_cache/response_codes')
async def patch_handler_response_codes(request: Request):
    try:
        ctx = json.loads(await request.json())
        _id = request.query_params.get('id')
        action = request.query_params.get('action')
        Validate.validate_object_id(_id)
        Validate.validate_schema(ctx, endpoint_cache_validator)
        if action == 'add':
            await EndpointCacher.add_status_codes(ctx['response_codes'], _id, DB.get_redis(request))
        elif action == 'remove':
            await EndpointCacher.remove_status_codes(ctx['response_codes'], _id, DB.get_redis(request))
        else:
            return resp_error_json(ERROR_PARAMETER_ERROR, msg='Invalid action provided')
        return resp_success_json(msg='Endpoint cache response codes updated')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.delete('/endpoint_cache')
async def delete_handler(request: Request):
    try:
        _id = request.query_params.get('id')
        Validate.validate_object_id(_id)
        await EndpointCacher.delete(_id, DB.get_redis(request))
        return resp_success_json(msg='Endpoint cache deleted')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.post('/endpoint_cache')
async def post_handler(request: Request):
    try:
        ctx = json.loads(await request.json())
        Validate.validate_schema(ctx, endpoint_cache_validator)
        await EndpointCacher.create(ctx, DB.get_redis(request), DB.get(request, service_controller.table))
        return resp_success_json(msg='Endpoint cache created')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))
