import asyncio
import typing
from typing import Optional

import aiohttp
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message, Update, UpdateObject, UpdateMessage
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.ts: Optional[int] = None
        self.random_id: Optional[int] = 0

    async def connect(self, app: "Application"):
        # TODO: добавить создание aiohttp ClientSession,
        #  получить данные о long poll сервере с помощью метода groups.getLongPollServer
        #  вызвать метод start у Poller
        async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            self.session = session
            self.poller = Poller(store=self.app.store)
            await self._get_long_poll_service()
            await self.poller.start()

    async def disconnect(self, app: "Application"):
        # TODO: закрыть сессию и завершить поллер
        await self.session.connector.close()
        await self.session.close()
        await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        async with self.session.get(
                self._build_query('https://api.vk.com/method/',
                                  'groups.getLongPollServer',
                                  params={'access_token': self.app.config.bot.group_token,
                                          'group_id': self.app.config.bot.group_id}
                                  )
        ) as response:
            json_data = await response.json()
            self.key = json_data['response']['key']
            self.server = json_data['response']['server']
            self.ts = json_data['response']['ts']

    async def poll(self):
        async with self.session.get(
                f'{self.server}?act=a_check&key={self.key}&ts={self.ts}&wait=25'
        ) as response:
            json_data = await response.json()
            self.ts = int(json_data['ts'])
            updates = json_data['updates']
            raw_updates = []
            for update in updates:
                raw_updates += [Update(update['type'],
                                       UpdateObject(UpdateMessage(
                                           from_id=update['object']['message']['from_id'],
                                           text=update['object']['message']['text'],
                                           id=update['object']['message']['id'])))]
            return raw_updates

    async def send_message(self, message: Message) -> None:
        async with self.session.post(
                self._build_query('https://api.vk.com/method/',
                                  'messages.send',
                                  params={'access_token': self.app.config.bot.group_token,
                                          'peer_id': 2000000001,
                                          'message': message.text,
                                          'random_id': self.random_id,
                                          'group_id': self.app.config.bot.group_id}
                                  )
        ) as response:
            self.random_id += 1
            print(f'HTTP Response Status: {response.status}')
            json_data = await response.json()
            print(json_data)
