from django.urls import path
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, CollectionViewSet, ItemViewSet,
    CollectionRatingViewSet, DuplicateFlagViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'collections', CollectionViewSet)
router.register(r'items', ItemViewSet)
router.register(r'ratings', CollectionRatingViewSet)
router.register(r'duplicates', DuplicateFlagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("items/add/", views.add_item, name="add_item")
]