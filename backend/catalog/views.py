import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Item, Collection

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
