import json
import multidict
import pydash
from bson import json_util
from fastapi import APIRouter
from fastapi import Request

from flash.circuit_breaker.schema import circuit_breaker_validator
from flash.common.error_code import ERROR_SERVER
from flash.common.resp import resp_error_json, resp_success_json
from flash.models.circuit_breaker import CircuitBreaker
from flash.service import controller as service_controller
from flash.util import DB, Bson
from flash.util.validate import Validate

router = APIRouter()
table = 'circuit_breaker'


@router.post('/circuit_breaker')
async def post_handler(request: Request):
    try:
        ctx = json.loads(await request.json())
        Validate.validate_schema(ctx, circuit_breaker_validator)
        await CircuitBreaker.create(circuit_breaker_validator.normalized(ctx), DB.get(request, table), DB.get(request, service_controller.table))
        return resp_success_json(msg='Circuit breaker created')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.get('/circuit_breaker')
async def get_handler(request: Request):
    try:
        circuit_breakers = None
        if len(request.keys()) == 0:
            circuit_breakers = await CircuitBreaker.get_all(DB.get(request, table))
        else:
            circuit_breakers = []
            if 'id' in request.query_params:
                Validate.validate_object_id(request.query_params.get('id'))
                circuit_breaker = await CircuitBreaker.get_by_id(request.query_params.get('id'), DB.get(request, table))
                if circuit_breaker is not None:
                    circuit_breakers.append(circuit_breaker)
            elif 'service_id' in request.query_params:
                Validate.validate_object_id(
                    request.query_params.get('service_id'))
                circuit_breakers = await CircuitBreaker.get_by_service_id(request.query_params.get('service_id'), DB.get(request, table))
            elif 'status_code' in request.query_params:
                circuit_breakers = await CircuitBreaker.get_by_status_code(int(request.query_params.get('status_code')), DB.get(request, table))
            elif 'method' in request.query_params:
                circuit_breakers = await CircuitBreaker.get_by_method(request.query_params.get('method'), DB.get(request, table))
            elif 'threshold' in request.query_params:
                circuit_breakers = await CircuitBreaker.get_by_threshold(float(request.query_params.get('threshold')), DB.get(request, table))
        return resp_success_json(msg='circuit created', data=DB.format_documents(Bson.to_json(circuit_breakers)))
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.patch('/circuit_breaker')
async def patch_handler(request: Request):
    try:
        ctx = json.loads(await request.json())
        circuit_breaker_id = request.query_params['id']
        Validate.validate_schema(ctx, circuit_breaker_validator)
        Validate.validate_object_id(circuit_breaker_id)
        await CircuitBreaker.update(circuit_breaker_id, pydash.omit(ctx, 'id'), DB.get(request, table))
        return resp_success_json(msg='Circuit breaker updated')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))

@router.delete('/circuit_breaker')
async def delete_handler(request: Request):
    try:
        Validate.validate_object_id(request.query_params.get('id'))
        await CircuitBreaker.remove(request.query_params.get('id'), DB.get(request, table))
        return resp_success_json(msg='Circuit breaker deleted')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))
