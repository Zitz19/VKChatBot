from aiohttp.web_exceptions import HTTPForbidden
from aiohttp_apispec import request_schema, response_schema, docs

from app.admin.models import Admin
from app.admin.schemes import AdminSchema, AdminResponseSchema
from app.web.app import View
from app.web.schemes import OkResponseSchema
from app.web.utils import json_response


class AdminLoginView(View):
    @docs(tags=['VKChat'], summary='Login Admin', description='Login admin')
    @request_schema(AdminSchema)
    @response_schema(AdminResponseSchema, 200)
    async def post(self):
        data = self.data
        email = data['email']
        password = data['password']
        admin = await self.request.app.base_accessor.get_admin(email)
        if admin is None:
            raise HTTPForbidden()
        if password == admin.password:
            return json_response(data={'id': admin.id, 'email': admin.email})
        else:
            raise HTTPForbidden()


class AdminCurrentView(View):
    async def get(self):
        raise NotImplementedError
