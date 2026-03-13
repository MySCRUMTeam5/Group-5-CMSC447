from django.urls import path
from . import views

urlpatterns = [
    path("items/add/", views.add_item, name="add_item"),
    path("items/delete/<int:collection_id>/<int:item_id>/", views.delete_item, name="delete_item"),
    path(
        "collections/<int:collection_id>/item-count/",
        views.get_collection_item_count,
        name="get_collection_item_count",
    ),
]