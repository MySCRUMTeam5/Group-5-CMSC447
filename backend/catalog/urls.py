from django.urls import path
from . import views

urlpatterns = [
    path("items/add/", views.add_item, name="add_item"),
    path("items/", views.items_view, name="items")
]