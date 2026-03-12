from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum
from .models import Collection


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
        return JsonResponse(
            {"error": "Collection not found"},
            status=404
        )