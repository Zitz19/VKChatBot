import hashlib

import aiohttp_session
from aiohttp.web_exceptions import HTTPForbidden, HTTPUnauthorized
from aiohttp_apispec import request_schema, response_schema, docs
from aiohttp_session import new_session, get_session

from app.admin.models import Admin
from app.admin.schemes import AdminSchema, AdminResponseSchema
from app.web.app import View
from app.web.schemes import OkResponseSchema
from app.web.utils import json_response, check_basic_auth


class AdminLoginView(View):
    @docs(tags=['VKChat'], summary='Login Admin', description='Login admin')
    @request_schema(AdminSchema)
    @response_schema(AdminResponseSchema, 200)
    async def post(self):
        data = self.data
        email = data['email']
        password = data['password']
        admin = await self.request.app.store.admins.get_by_email(email)
        if admin is None:
            raise HTTPForbidden()
        if hashlib.sha256(password.encode()).hexdigest() == admin.password:
            session = await aiohttp_session.new_session(request=self.request)
            session['key'] = admin.email
            return json_response(data={'id': admin.id, 'email': admin.email})
        else:
            raise HTTPForbidden()


class AdminCurrentView(View):
    @docs(tags=['VKChat'], summary='Current User', description='Current user')
    @response_schema(AdminResponseSchema, 200)
    async def get(self):
        session = await get_session(self.request)
        if not session:
            raise HTTPUnauthorized
        user = await self.store.admins.get_by_email(session['key'])
        if not user or session['key'] != user.email:
            raise HTTPForbidden
        else:
            return json_response(data={'id': user.id,
                                       'email': user.email})
