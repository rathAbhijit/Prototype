class RoomManager:
    def __init__(self):
        self.rooms = {}

    def create_or_get_room(self, room_id):
        from .models import Room, File

        if room_id not in self.rooms:
            room_obj, _ = Room.objects.get_or_create(room_id=room_id)

            files_qs = File.objects.filter(room=room_obj)

            if not files_qs.exists():
                File.objects.create(
                    room=room_obj,
                    name="main.txt",
                    content=""
                )

            files = {
                f.name: f.content for f in File.objects.filter(room=room_obj)
            }

            self.rooms[room_id] = {
                "files": files,
                "users": set()
            }

        return self.rooms[room_id]

    def add_user(self, room_id, channel_name):
        room = self.create_or_get_room(room_id)
        room["users"].add(channel_name)

    def remove_user(self, room_id, channel_name):
        if room_id in self.rooms:
            self.rooms[room_id]["users"].discard(channel_name)

    def update_file(self, room_id, filename, content):
        from .models import Room, File

        room = self.create_or_get_room(room_id)

        room["files"][filename] = content

        room_obj = Room.objects.get(room_id=room_id)

        file_obj, _ = File.objects.get_or_create(
            room=room_obj,
            name=filename,
            defaults={"content": ""}
        )

        file_obj.content = content
        file_obj.save()

    def create_file(self, room_id, filename):
        from .models import Room, File

        room = self.create_or_get_room(room_id)

        if filename not in room["files"]:
            room["files"][filename] = ""

            room_obj, _ = Room.objects.get_or_create(room_id=room_id)

            File.objects.get_or_create(
                room=room_obj,
                name=filename,
                defaults={"content": ""}
            )