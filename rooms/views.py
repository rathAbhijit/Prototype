from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Room, Node


def build_tree(nodes, parent=None):
    branch = []

    for node in nodes:
        if node.parent_id == parent:
            branch.append({
                "id": node.id,
                "name": node.name,
                "type": node.node_type,
                "children": build_tree(nodes, node.id)
            })

    return branch


@api_view(["GET"])
def get_tree(request, room_id):

    room, _ = Room.objects.get_or_create(room_id=room_id)

    nodes = Node.objects.filter(room=room)

    tree = build_tree(nodes)

    return Response(tree)


@api_view(["POST"])
def create_node(request, room_id):

    room = Room.objects.get(room_id=room_id)

    node = Node.objects.create(
        room=room,
        name=request.data["name"],
        node_type=request.data["type"],
        parent_id=request.data.get("parent")
    )

    return Response({
        "id": node.id,
        "name": node.name,
        "type": node.node_type
    })


@api_view(["PATCH"])
def rename_node(request, node_id):

    node = Node.objects.get(id=node_id)

    node.name = request.data["name"]

    node.save()

    return Response({"status": "renamed"})


@api_view(["DELETE"])
def delete_node(request, node_id):

    node = Node.objects.get(id=node_id)

    node.delete()

    return Response({"status": "deleted"})


@api_view(["GET"])
def get_file_content(request, node_id):

    node = Node.objects.get(id=node_id, node_type="file")

    return Response({
        "content": node.content
    })


@api_view(["POST"])
def save_file_content(request, node_id):

    node = Node.objects.get(id=node_id, node_type="file")

    node.content = request.data["content"]

    node.save()

    return Response({
        "status": "saved"
    })