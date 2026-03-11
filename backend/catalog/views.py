from django.shortcuts import render
from django.http import JsonResponse
from backend.catalog.models import Item

# Create your views here.
def delete_item(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
        item_name = item.name
        item.delete()        
        return JsonResponse({"message": f"Item: '{item_name}' deleted successfully."})
    except Item.DoesNotExist:
        return JsonResponse({"error": "Item not found."}, status=404)
        