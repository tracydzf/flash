import pydash
from aiohttp import web


class Error:
    @staticmethod
    def handle(err: Exception) -> web.Response:
        """
        handles exceptions in controllers

        @param err: (Exception) error to handle
        @returns: json respone
        """
        err_ctx = err.args[0]
        if pydash.has(err_ctx, 'status_code') is True:
            return web.json_response(err_ctx, status=err_ctx['status_code'])
        else:
            return web.json_response({
                'message': err_ctx,
                'status_code': 500
            }, status=500)
