import json
import pydash
from bson import json_util
from fastapi import APIRouter
from fastapi import Request

from flash.common.error_code import ERROR_SERVER
from flash.common.resp import resp_error_json, resp_success_json
from flash.models.request_validator import RequestValidator
from flash.request_validator.schema import request_validator
from flash.service import controller as service_controller
from flash.util import DB, Bson
from flash.util.validate import Validate

router = APIRouter()
table = 'request_validator'


@router.get('/request_validator')
async def get_handler(request: Request):
    try:
        response = []
        if 'service_id' in request.query_params:
            Validate.validate_object_id(request.query_params['service_id'])
            service_id = request.query_params['service_id']
            response = await RequestValidator.get_by_service_id(service_id, DB.get(request, table))
        elif 'id' in request.query_params:
            Validate.validate_object_id(request.query_params.get('id'))
            req_validator = await RequestValidator.get_by_id(request.query_params.get('id'), DB.get(request, table))
            if req_validator is not None:
                response.append(req_validator)
        elif 'method' in request.query_params:
            method = request.query_params['method']
            response = await RequestValidator.get_by_method(method, DB.get(request, table))
        else:
            response = await RequestValidator.get_all(DB.get(request, table))
        return resp_success_json(msg='service created', data=Bson.to_json(response))
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.post('/request_validator')
async def create_handler(request: Request):
    try:
        body = json.loads(await request.json())
        Validate.validate_schema(body, request_validator)
        await RequestValidator.create(request_validator.normalized(body), DB.get(request, table),
                                      DB.get(request, service_controller.table))

        return resp_success_json(msg='Request validator created')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.patch('/request_validator')
async def update_handler(request: Request):
    try:
        id = request.query_params['id']
        body = json.loads(await request.json())
        Validate.validate_object_id(id)
        Validate.validate_schema(body, request_validator)
        await RequestValidator.update(id, body, DB.get(request, table))
        return resp_success_json(msg='request validator updated')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.delete('/request_validator')
async def delete_handler(request: Request):
    try:
        id = request.query_params.get('id')
        Validate.validate_object_id(id)
        await RequestValidator.delete(id, DB.get(request, table))
        return resp_success_json(msg='request validator deleted')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))
