import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets
from .models import User, Collection, Item, CollectionRating, DuplicateFlag
from .serializers import (
    UserSerializer, CollectionSerializer, ItemSerializer,
    CollectionRatingSerializer, DuplicateFlagSerializer
)

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
        return JsonResponse({"message": f"Item: '{item_name}' deleted successfully!"})
    except Item.DoesNotExist:
        return JsonResponse({"error": "Item not deleted. Item not found in this collection!"}, status=404)

@require_http_methods(['"GET'])
def sort_filter_collection(request):  
    if request.method != 'GET':
        return JsonResponse({"Error": "Method not allowed"}, status = 405)
    
    sort = request.GET.get("sort")
    
    filter_val = request.GET.get("filter")

    #DO WE WANT ANY OTHER SORT FEATURES?
    #Names may need to be changed based on how we store our data in the database
    sort_dict = {
        "p_price_ascend" : "purchase_price",
        "p_price_descend" : "-purchase_price",
        "alpha_ascend" : "alpha",
        "alpha_descend" : "-alpha",
        "date_ascend" : "purchase_date",
        "date_descend" : "-purchase_date"
    }

    #Right now, doing filter by preset buttons, may move to user input later
    #only doing one filter rn
    filter_dict = {
        "price_below" : ("price__lt", 10),
        "price_above" : ("price__gt", 10),
        "price_equal" : ("price", 10),
        "name" : ("name__contains", None)
    }

    con = sqlite3.connect("collection.db") #may need to change this name later

    cur = con.cursor()

    sort_by = sort_dict.get(sort)

    filter_by = filter_dict.get(filter_val)

    data = Item.objects.all()
    
    if sort and sort_by:
        data = Item.objects.all().order_by(sort_by).values()
    
    if filter_val and filter_by:
        data = Item.objects.filter(**{filter_by})
    
    if not sort_by or not filter_by:
        return JsonResponse({"Error": "Not a valid sort/filter option"}, status = 404)
    
    return JsonResponse(list(data.values(), safe=False, status=200))

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
