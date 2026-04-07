from rest_framework import serializers
from .models import User, Collection, Item, CollectionRating, DuplicateFlag

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'profile_picture']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class CollectionSerializer(serializers.ModelSerializer):
    # This lets us see the actual items inside the collection
    items = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = [
            'id', 'owner', 'name', 'description', 'category', 'collection_type',
            'created_at', 'updated_at', 'is_public', 'item_count', 
            'total_value', 'items'
        ]

class CollectionRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionRating
        fields = '__all__'

class DuplicateFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DuplicateFlag
        fields = '__all__'
