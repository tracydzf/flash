import json

import pydash
from fastapi import APIRouter
from fastapi import Request
from flash.common.error_code import ERROR_SERVER
from flash.common.resp import resp_error_json, resp_success_json
from flash.event.schema import event_validator
from flash.models.event import Event
from flash.util import DB, Bson
from flash.util.validate import Validate
from flash.circuit_breaker import controller as circuit_breaker_controller

router = APIRouter()
table = 'event'


@router.post('/event')
async def post_handler(request: Request):
    try:
        ctx = json.loads(await request.json())
        Validate.validate_schema(ctx, event_validator)
        await Event.create(ctx, DB.get(request, table), DB.get(request, circuit_breaker_controller.table))
        return resp_success_json(msg='Event created')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.get('/event')
async def get_handler(request: Request):
    try:
        services = []
        if len(request.keys()) == 0:
            services = await Event.get_all(DB.get(request, table))
        else:
            if 'id' in request.query_params:
                Validate.validate_object_id(request.query_params.get('id'))
                service = await Event.get_by_id(request.query_params.get('id'), DB.get(request, table))
                if service is not None:
                    services.append(service)
            elif 'circuit_breaker_id' in request.query_params:
                Validate.validate_object_id(
                    request.query_params.get('circuit_breaker_id'))
                services = await Event.get_by_circuit_breaker_id(request.query_params.get('circuit_breaker_id'),
                                                                 DB.get(request, table))
            elif 'target' in request.query_params:
                services = await Event.get_by_target(request.query_params.get('target'), DB.get(request, table))
        return resp_success_json(msg='service created', data=DB.format_documents(Bson.to_json(services)))
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.patch('/event')
async def patch_handler(request: Request):
    try:
        ctx = json.loads(await request.json())
        event_id = request.query_params['id']
        Validate.validate_object_id(event_id)
        Validate.validate_schema(ctx, event_validator)
        await Event.update(event_id, pydash.omit(ctx, '_id'), DB.get(request, table))
        return resp_success_json(msg='event updated')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.delete('/event')
async def delete_handler(request: Request):
    try:
        Validate.validate_object_id(request.query_params.get('id'))
        await Event.remove(request.query_params.get('id'), DB.get(request, table))
        return resp_success_json(msg='Service deleted')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))
