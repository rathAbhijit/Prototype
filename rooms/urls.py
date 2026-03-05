from django.urls import path
from . import views


urlpatterns = [

    path("<str:room_id>/tree/", views.get_tree),

    path("<str:room_id>/create-node/", views.create_node),

    path("rename/<int:node_id>/", views.rename_node),

    path("delete/<int:node_id>/", views.delete_node),

    path("content/<int:node_id>/", views.get_file_content),

    path("save/<int:node_id>/", views.save_file_content),

]