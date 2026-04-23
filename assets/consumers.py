from __future__ import annotations

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class AssetConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('assets', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('assets', self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        pass

    async def asset_update(self, event):
        await self.send(text_data=json.dumps(event['data']))
