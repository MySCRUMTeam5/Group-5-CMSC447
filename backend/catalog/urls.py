from django.urls import path
from . import views

urlpatterns = [
  path(
    "collections/<int:collection_id>/item-count/",
    views.get_collection_item_count,
    name="get_collection_item_count",
),
]