import base64
import hashlib
from typing import Any, Optional

from aiohttp.web import json_response as aiohttp_json_response
from aiohttp.web_response import Response

from app.admin.models import Admin
from app.store import AdminAccessor


def json_response(data: Any = None, status: str = "ok") -> Response:
    if data is None:
        data = {}
    return aiohttp_json_response(
        data={
            "status": status,
            "data": data,
        }
    )


def error_json_response(
        http_status: int,
        status: str = "error",
        message: Optional[str] = None,
        data: Optional[dict] = None,
):
    if data is None:
        data = {}
    return aiohttp_json_response(
        status=http_status,
        data={
            'status': status,
            'message': str(message),
            'data': data,
        })


async def check_basic_auth(raw_credentials: str, accessor: AdminAccessor) -> Optional[Admin]:
    parts = raw_credentials.split(':')
    if len(parts) != 2:
        return None
    user: Optional[Admin, None] = await accessor.get_by_email(parts[0])
    if not user:
        return None
    if parts[0] == user.email and hashlib.sha256(parts[1].encode()).hexdigest() == user.password:
        return user
    return None
