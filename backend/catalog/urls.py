from django.urls import path
from . import views

urlpatterns = [path("items/delete/<int:collection_id>/<int:item_id>/", views.delete_item, name="delete_item"),
]