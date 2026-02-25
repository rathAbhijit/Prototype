from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from rooms.services import room_manager
from .sync import apply_last_write_wins


class EditorConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"editor_{self.room_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # DB-safe room loading
        room = await database_sync_to_async(
            room_manager.create_or_get_room
        )(self.room_id)

        room_manager.add_user(self.room_id, self.channel_name)

        await self.accept()

        await self.send(json.dumps({
            "type": "file_list_update",
            "files": list(room["files"].keys())
        }))

        if room["files"]:
            first_file = list(room["files"].keys())[0]
            await self.send(json.dumps({
                "type": "code_update",
                "payload": {
                    "filename": first_file,
                    "code": room["files"][first_file]
                },
                "sender": None
            }))

        await self.broadcast_user_count()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        room_manager.remove_user(self.room_id, self.channel_name)
        await self.broadcast_user_count()


    async def receive(self, text_data):
        event = json.loads(text_data)

        room = await database_sync_to_async(
            room_manager.create_or_get_room
        )(self.room_id)

        event_type = event.get("type")

        # CODE UPDATE
        if event_type == "code_update":
            filename = event["payload"]["filename"]
            new_code = event["payload"]["code"]
            sender = event.get("sender")

            current_code = room["files"].get(filename, "")
            updated_code = apply_last_write_wins(current_code, new_code)

            await database_sync_to_async(
                room_manager.update_file
            )(self.room_id, filename, updated_code)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "broadcast_code",
                    "filename": filename,
                    "code": updated_code,
                    "sender": sender,
                }
            )

        # FILE CREATE
        elif event_type == "file_create":
            filename = event["payload"]["filename"]

            if filename and filename not in room["files"]:
                await database_sync_to_async(
                    room_manager.create_file
                )(self.room_id, filename)

                room = await database_sync_to_async(
                    room_manager.create_or_get_room
                )(self.room_id)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "file_list_update",
                        "files": list(room["files"].keys())
                    }
                )

        # FILE OPEN
        elif event_type == "file_open":
            filename = event["payload"]["filename"]
            file_content = room["files"].get(filename, "")

            await self.send(json.dumps({
                "type": "code_update",
                "payload": {
                    "filename": filename,
                    "code": file_content
                },
                "sender": None
            }))


    async def broadcast_code(self, event):
        await self.send(json.dumps({
            "type": "code_update",
            "payload": {
                "filename": event["filename"],
                "code": event["code"]
            },
            "sender": event.get("sender")
        }))


    async def file_list_update(self, event):
        await self.send(json.dumps({
            "type": "file_list_update",
            "files": event["files"]
        }))


    async def broadcast_user_count(self):
        user_count = len(
            room_manager.rooms.get(self.room_id, {}).get("users", [])
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "presence_update",
                "count": user_count
            }
        )


    async def presence_update(self, event):
        await self.send(json.dumps({
            "type": "presence_update",
            "count": event["count"]
        }))