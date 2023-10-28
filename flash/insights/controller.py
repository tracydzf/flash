import json
import pydash
from fastapi import APIRouter
from fastapi import Request
from .schema import insights_validator
from ..common.error_code import ERROR_SERVER
from ..common.resp import resp_error_json, resp_success_json
from ..models.insights import Insights
from ..util import DB, Bson
from ..util.validate import Validate
from flash.service import controller as service_controller

router = APIRouter()
table = 'insights'


@router.post('/insights')
async def post_handler(request: Request):
    try:
        body = json.loads(await request.json())
        Validate.validate_schema(body, insights_validator)
        await Insights.create(body, DB.get(request, table), DB.get(request, service_controller.table))
        return resp_success_json(msg='Insight created')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.get('/insights')
async def get_handler(request: Request):
    try:
        if len(request.keys()) == 0:
            insights = await Insights.get_all(DB.get(request, table))
        else:
            insights = []
            if 'id' in request.query_params:
                insight = await Insights.get_by_id(request.query_params.get('id'), DB.get(request, table))
                if insight is not None:
                    insights.append(insight)
            elif 'remote_ip' in request.query_params:
                insights = await Insights.get_by_remote_ip(request.query_params.get('remote_ip'),
                                                           DB.get(request, table))
            elif 'status_code' in request.query_params:
                insights = await Insights.get_by_status_code(request.query_params.get('status_code', 0),
                                                             DB.get(request, table))
            elif 'path' in request.query_params:
                insights = await Insights.get_by_path(request.query_params.get('path'), DB.get(request, table))
            elif 'method' in request.query_params:
                insights = await Insights.get_by_method(request.query_params.get('method'), DB.get(request, table))
            elif 'service_id' in request.query_params:
                insights = await Insights.get_by_service_id(request.query_params.get('service_id'),
                                                            DB.get(request, table))
            elif 'scheme' in request.query_params:
                insights = await Insights.get_by_scheme(request.query_params.get('scheme'), DB.get(request, table))
        return resp_success_json(msg='service created', data=DB.format_documents(Bson.to_json(insights)))
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.patch('/insights')
async def patch_handler(request: Request):
    try:
        ctx = json.loads(await request.json())
        service_id = request.query_params['id']
        Validate.validate_object_id(service_id)
        Validate.validate_schema(ctx, insights_validator)
        await Insights.update(service_id, pydash.omit(ctx, 'id'), DB.get(request, table))
        return resp_success_json(msg='insight updated')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))


@router.delete('/insights')
async def delete_handler(request: Request):
    try:
        service_id = request.query_params.get('id')
        Validate.validate_object_id(service_id)
        await Insights.remove(service_id, DB.get(request, table))
        return resp_success_json(msg='insight deleted')
    except Exception as err:
        return resp_error_json(ERROR_SERVER, msg=str(err))
