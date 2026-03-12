from django.shortcuts import render
from django.http import JsonResponse
from backend.catalog.models import Item
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

def delete_item(request, collection_id, item_id):
    try:
        item = Item.objects.get(id=item_id, collection_id=collection_id)
        item_name = item.name
        item.delete()        
        return JsonResponse({"message": f"Item: '{item_name}' deleted successfully!"})
    except Item.DoesNotExist:
        return JsonResponse({"error": "Item not deleted. Item not found in this collection!"}, status=404)