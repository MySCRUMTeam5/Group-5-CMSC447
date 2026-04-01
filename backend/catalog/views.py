import json
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Sum
from rest_framework import viewsets
from .models import User, Collection, Item, CollectionRating, DuplicateFlag
from .serializers import (
    UserSerializer, CollectionSerializer, ItemSerializer,
    CollectionRatingSerializer, DuplicateFlagSerializer
)    

User = get_user_model() #until we set up auth

@csrf_exempt
@require_http_methods(["POST", "GET"])
def add_get_collections(request):
    if request.method == "GET":
        collections = Collection.objects.all()

        data = []

        for c in collections:
            data.append({
                "id" : c.id,
                "name" : c.name,
                "description" : c.description,
                "category": c.category,
                "type": c.collection_type,
                "is_public": c.is_public,
                "itemCount": c.item_count,
                "totalValue": c.total_value,
            })
        
        return JsonResponse(data, safe=False)

    elif request.method == "POST":
        data = json.loads(request.body)

        if "name" not in data:
            return JsonResponse({"Error" : "Collection must have a name"}, status=400)

        if request.user.is_authenticated:
            user = request.user
        
        else:
            user = User.objects.first()
        
        collection = Collection.objects.create(
            owner=user,
            name=data["name"],
            description=data.get("description",""),
            category=data.get("category", ""),
            collection_type=data.get("type", "video_games"),
            is_public=data.get("is_public", False)
            )

        return JsonResponse({
            "id" : collection.id,
            "name" : collection.name,
            "description" : collection.description,
            "category": collection.category,
            "type": collection.collection_type,
            "is_public": collection.is_public,
            "itemCount": collection.item_count,
            "totalValue": collection.total_value,
            }, status=201)
        


@csrf_exempt
@require_http_methods(["POST"])
def add_item(request):
    try:
        data = json.loads(request.body)
        if "collection_id" not in data or "name" not in data:
            return JsonResponse({"error": "collection_id and name are required"}, status=400)
        try:
            collection = Collection.objects.get(id=data["collection_id"])
        except Collection.DoesNotExist:
            return JsonResponse({"error": "Collection not found"}, status=404)

        item = Item.objects.create(
            collection=collection,
            name=data["name"],
            description=data.get("description", ""),
            category=data.get("category", ""),
            condition=data.get("condition", "good"),
            quantity=data.get("quantity", 1),
            barcode=data.get("barcode", ""),
            purchase_price=data.get("purchase_price", 0),
            current_value=data.get("current_value", 0),
            purchase_date=data.get("purchase_date", None),
            usage_status=data.get("usage_status", "stored"),
            listing_status=data.get("listing_status", "not_for_sale"),
            asking_price=data.get("asking_price", 0),
            is_special_edition=data.get("is_special_edition", False),
            edition_details=data.get("edition_details", ""),
        )

        return JsonResponse({
            "message": "Item added successfully",
            "item": {
                "id": item.id,
                "collection_id": item.collection.id,
                "name": item.name,
                "description": item.description,
                "category": item.category,
                "condition": item.condition,
                "quantity": item.quantity,
                "barcode": item.barcode,
                "purchase_price": str(item.purchase_price),
                "current_value": str(item.current_value),
                "purchase_date": str(item.purchase_date) if item.purchase_date else None,
                "usage_status": item.usage_status,
                "listing_status": item.listing_status,
                "asking_price": str(item.asking_price),
                "is_special_edition": item.is_special_edition,
                "edition_details": item.edition_details,
                "created_at": item.created_at.isoformat(),
            }
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_item(request, collection_id, item_id):
    try:
        item = Item.objects.get(id=item_id, collection_id=collection_id)
        item_name = item.name
        item.delete()
        return JsonResponse(
            {"message": f"Item: '{item_name}' deleted successfully!"},
            status=200
        )
    except Item.DoesNotExist:
        return JsonResponse(
            {"error": "Item not deleted. Item not found in this collection!"},
            status=404
        )


@require_http_methods(["GET"])
def get_collection_item_count(request, collection_id):
    try:
        collection = Collection.objects.get(id=collection_id)

        total_items = collection.items.aggregate(
            total=Sum("quantity")
        )["total"] or 0

        return JsonResponse({
            "collection_id": collection_id,
            "collection_name": collection.name,
            "total_items": total_items
        })

    except Collection.DoesNotExist:
        return JsonResponse({"error": "Collection not found"}, status=404)

@require_http_methods(['GET'])
def sort_filter_collection(request):
    if request.method != 'GET':
        return JsonResponse({"Error": "Method not allowed"}, status = 405)
    
    sort = request.GET.get("sort") #gets what value to sort by
    
    filter_val = request.GET.get("filter") #gets what value to filter by

    item_type = request.GET.get("type") #gets the item type that we are filtering/sorting by

    #sets up different dictionaries based on what item collection we are filtering
    VIDEO_GAMES_FILTER_FIELDS = {
        "playStatus" : "play_status__iexact",
        "platform" : "platform__iexact",
        "genre" : "genre__iexact",
        "completeness" : "completeness,__iexact",
        }

    TRADING_CARDS_FILTER_FIELDS = {
        "series" : "series__iexact",
        "grade" : "grade__iexact"
        }

    COMICS_FILTER_FIELDS = {
        "publisher" : "publisher__iexact",
        "readStatus" : "read_status__iexact",
        "grade" : "grade__iexact",
        "readStatus" : "read_status__iexact"
        }

    FUNKO_FILTER_FIELDS = {
        "series" : "series__iexact",
        "completeness" : "completeness__iexact",
        "exclusive" : "exclusive__iexact"
        }
    
    LEGO_FILTER_FIELDS = {
        "series" : "series__iexact",
        "completeness" : "completness__iexact"
        }

    SPORTS_CARDS_FILTER_FIELDS = {
        "sport" : "sport__iexact",
        "grade" : "grade__iexact"
    }

    MUSIC_FILTER_FIELDS = {
        "format" : "format__iexact",
        "genre" : "genre__iexact"
    }

    MOVIES_FILTER_FIELDS = {
        "watchedStatus" : "watched_status__iexact",
        "format" : "format__iexact",
        "genre" : "genre__iexact"
    }

    FILTER_ITEM_TYPES = {
        "games" : VIDEO_GAMES_FILTER_FIELDS,
        "trading_cards" : TRADING_CARDS_FILTER_FIELDS,
        "comics" : COMICS_FILTER_FIELDS,
        "funko" : FUNKO_FILTER_FIELDS,
        "lego" : LEGO_FILTER_FIELDS,
        "sports_cards" : SPORTS_CARDS_FILTER_FIELDS,
        "music" : MUSIC_FILTER_FIELDS,
        "movies" : MOVIES_FILTER_FIELDS
    }

    SORT_ITEMS = {
        "p_price_ascend" : "purchase_price",
        "p_price_descend" : "-purchase_price",
        "alpha_ascend" : "name",
        "alpha_descend" : "-name",
        "date_ascend" : "purchase_date",
        "date_descend" : "-purchase_date"
    }

    data = Item.objects.all()
    
    if sort:
        sort_by = SORT_ITEMS.get(sort)
        if not sort_by:
            return JsonResponse({"Error" : "Not a valid sort option"}, status=404)
        data = data.order_by(sort_by)
    
    if filter_val:
        filter_type = FILTER_ITEM_TYPES.get(item_type) #gets the correct item from ITEM_TYPES dict

        filter_by = filter_type.get(filter_val) #gets the correct key val pair from specified dict
        #based on type specified from filter_type

        if not filter_by:
            return JsonResponse({"Error" : "Not a valid filter option"}, status=404)
        data = Item.objects.filter(**{filter_by : value})
    
    return JsonResponse(list(data.values()), safe=False, status=200)


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