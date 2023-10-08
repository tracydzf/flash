import json

from aiohttp import web
from fastapi import APIRouter

from flash.common.error_code import ERROR_PARAMETER_ERROR, ERROR_SERVER
from flash.common.resp import resp_success_json, resp_error_json
from flash.service.schema import service_validator
from flash.util import DB, Bson
from flash.util.error import Error
from flash.util.validate import Validate
from flash.models.service import Service
from fastapi import Request

router = APIRouter()

table = 'service'


@router.post('/service')
async def post_handler(request: Request):
    try:
        print(await request.json())
        ctx = await request.json()

        Validate.validate_schema(ctx, service_validator)
        await Service.create(service_validator.normalized(ctx), DB.get(request, table))
        return resp_success_json(msg='service created')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.get('/service')
async def get_handler(request: Request):
    try:
        if len(request.keys()) == 0:
            services = await Service.get_all(DB.get(request, table))
            return web.json_response({
                'data': DB.format_documents(Bson.to_json(services)),
                'status_code': 200
            })
        else:
            services = []
            if 'id' in request.query_params:
                Validate.validate_object_id(request.query_params.get('id'))
                service = await Service.get_by_id(request.query_params.get('id'), DB.get(request, table))
                if service is not None:
                    services.append(service)
            elif 'state' in request.query_params:
                services = await Service.get_by_state(request.query_params.get('state'), DB.get(request, table))
            elif 'secure' in request.query_params:
                services = await Service.get_by_secure(bool(request.query_params.get('secure')),
                                                       DB.get(request, table))

            return resp_success_json(msg='service created', data=DB.format_documents(Bson.to_json(services)))
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.patch('/service')
async def patch_handler(request: Request):
    try:
        ctx = await request.json()
        service_id = request.query_params.get('id')
        Validate.validate_object_id(service_id)
        Validate.validate_schema(ctx, service_validator)
        await Service.update(service_id, ctx, DB.get(request, table))

        return resp_success_json(msg='service updated')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.delete('/service')
async def delete_handler(request: Request):
    try:
        Validate.validate_object_id(request.query_params.get('id'))
        await Service.remove(request.query_params.get('id'), DB.get(request, table))
        return resp_success_json(msg='service deleted')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))
