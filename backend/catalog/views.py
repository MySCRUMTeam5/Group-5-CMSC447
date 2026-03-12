from rest_framework import viewsets
from .models import User, Collection, Item, CollectionRating, DuplicateFlag
from .serializers import (
    UserSerializer, CollectionSerializer, ItemSerializer, 
    CollectionRatingSerializer, DuplicateFlagSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class CollectionRatingViewSet(viewsets.ModelViewSet):
    queryset = CollectionRating.objects.all()
    serializer_class = CollectionRatingSerializer

class DuplicateFlagViewSet(viewsets.ModelViewSet):
    queryset = DuplicateFlag.objects.all()
    serializer_class = DuplicateFlagSerializer
