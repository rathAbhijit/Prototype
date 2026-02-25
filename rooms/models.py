from django.db import models


class Room(models.Model):
    room_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.room_id


class File(models.Model):
    room = models.ForeignKey(Room, related_name="files", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    content = models.TextField(blank=True)

    def __str__(self):
        return f"{self.room.room_id} - {self.name}"
