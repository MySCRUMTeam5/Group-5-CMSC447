from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, CollectionViewSet, ItemViewSet,
    CollectionRatingViewSet, DuplicateFlagViewSet,
    barcode, get_wishlist, add_wishlist_item, delete_wishlist_item
)
from . import views


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'collections', CollectionViewSet)
router.register(r'items', ItemViewSet)
router.register(r'ratings', CollectionRatingViewSet)
router.register(r'duplicates', DuplicateFlagViewSet)

urlpatterns = [
    path("collections/", views.add_get_collections, name="add_get_collections"),
    path("collections/<int:collection_id>/items/", views.get_items, name="get_items"),
    path("items/add/", views.add_item, name="add_item"),
    path("items/delete/<int:collection_id>/<int:item_id>/", views.delete_item, name="delete_item"),
    path(
        "collections/<int:collection_id>/item-count/",
        views.get_collection_item_count,
        name="get_collection_item_count",
    ),
    path("items/", views.sort_filter_collection, name="sort_filter_collection"),
    path("barcode/", barcode, name="barcode"),
    path("wishlist/", get_wishlist, name="get_wishlist"),
    path("wishlist/add/", add_wishlist_item, name="add_wishlist_item"),
    path("wishlist/delete/<int:item_id>/", delete_wishlist_item, name="delete_wishlist_item"),
    path("", include(router.urls))
]