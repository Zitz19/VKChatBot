import typing
from logging import getLogger

from app.admin.models import Admin

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BaseAccessor:
    def __init__(self, app: "Application", *args, **kwargs):
        self.app = app
        self.logger = getLogger("accessor")
        app.on_startup.append(self.connect)
        app.on_cleanup.append(self.disconnect)

    async def connect(self, app: "Application"):
        await self.add_admin(Admin(1,
                                   self.app.config.admin.email,
                                   self.app.config.admin.password))
        print('connected to database')
        return

    async def disconnect(self, app: "Application"):
        self.app = None
        print('disconnected from database')
        return

    async def add_admin(self, admin: Admin):
        self.app.database.admins.append(admin)

    async def get_admin(self, email: str):
        for admin in self.app.database.admins:
            if admin.email == email:
                return admin
        return None
