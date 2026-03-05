from django.db import models


class Room(models.Model):
    room_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.room_id


class Node(models.Model):
    NODE_TYPES = (
        ("file", "File"),
        ("folder", "Folder"),
    )

    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    node_type = models.CharField(max_length=10, choices=NODE_TYPES)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children"
    )

    content = models.TextField(blank=True)

    class Meta:
        unique_together = ("room", "parent", "name")

    def __str__(self):
        return f"{self.name} ({self.node_type})"