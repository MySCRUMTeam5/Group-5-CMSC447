import json
import re
import requests
from datetime import timedelta, date
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Sum
from rest_framework import viewsets
from pyzbar.pyzbar import decode
from PIL import Image, UnidentifiedImageError
from .ebay_api import Ebay_API
from .ebay_api import Ebay_API
from .models import (
    Collection, Item, CollectionRating, DuplicateFlag,
    VideoGameItem, TradingCardItem, ComicItem, FunkoPopItem,
    LegoSetItem, SportsCardItem, MusicItem, MovieItem, WishlistItem,
    ValueSnapshot
)

from .serializers import (
    UserSerializer, CollectionSerializer, ItemSerializer,
    CollectionRatingSerializer, DuplicateFlagSerializer
)

User = get_user_model()

# ─── Maps collection_type to its model and accepted fields ───
COLLECTION_TYPE_CONFIG = {
    "video_games": {
        "model": VideoGameItem,
        "fields": ["platform", "genre", "completeness", "play_status"],
    },
    "trading_cards": {
        "model": TradingCardItem,
        "fields": ["series", "set_name", "card_number", "grade"],
    },
    "comics": {
        "model": ComicItem,
        "fields": ["publisher", "issue_title", "issue_number", "grade", "read_status"],
    },
    "funko_pops": {
        "model": FunkoPopItem,
        "fields": ["series", "box_number", "completeness", "exclusive"],
    },
    "lego_sets": {
        "model": LegoSetItem,
        "fields": ["series", "set_number", "completeness", "piece_count"],
    },
    "sports_cards": {
        "model": SportsCardItem,
        "fields": ["sport", "player_name", "card_number", "year", "grade"],
    },
    "music": {
        "model": MusicItem,
        "fields": ["artist", "album_title", "format", "genre"],
    },
    "movies": {
        "model": MovieItem,
        "fields": ["title", "format", "genre", "director", "watched_status"],
    },
}

def get_or_create_user(clerk_user_id, email=None):
    username = email or clerk_user_id

    if not username:
        raise ValueError("username resolved to empty/None")

    try:
        user = User.objects.get(clerk_user_id=clerk_user_id)
    except User.DoesNotExist:
        user = User.objects.create(
            clerk_user_id=clerk_user_id,
            username=username
        )

    return user

@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def edit_existing_item(request, item_id, collection_id):
    #make sure the item exists before editing
    try:
        data = json.loads(request.body)
        
        item_name = data.get("name")

        if not item_id or not item_name:
            return JsonResponse({"Error" : "Missing required fields"}, status=404)

        #get the item
        try:
            item = Item.objects.get(id=item_id)
        
        except Item.DoesNotExist:
            return JsonResponse({"Error" : "Item not found"}, status=404)

        #update the fields you want to edit
        item.name = item_name

        if "description" in data:
            item.description = data["description"]
        
        if "condition" in data:
            item.condition = data["condition"]
        
        if "collection_type" in data:
            item.collection_type = data["collection_type"]

        if "category" in data:
            item.category = data["category"]    
        
        if "purchase_price" in data:
            item.purchase_price = data["purchase_price"]
        
        if "usage_status" in data:
            item.usage_status = data["usage_status"]

        if "current_value" in data:
            item.current_value = data["current_value"]
        
        item.save()

        # update today's value for this collection
        today = date.today()
        total = item.collection.items.aggregate(total=Sum("current_value"))["total"] or 0
        ValueSnapshot.objects.update_or_create(
            collection=item.collection,
            date=today,
            defaults={"total_value": total}
        )

        return JsonResponse({"Message" : "Item updated successfully"})
    
    except json.JSONDecodeError:
        return JsonResponse({"Error" : "Invalid JSON format"}, status=400)


@csrf_exempt
@require_http_methods(["POST", "GET"])
def add_item_to_wishlist(request):
    print("🔥 HIT ADD ITEM ENDPOINT")

    if request.method == "POST":
        data = json.loads(request.body)

        clerk_user_id = data.get("clerk_user_id")

        if not clerk_user_id:
            return JsonResponse({"Error" : "Missing authentication (clerk id)"}, status=400)

        user = get_or_create_user(clerk_user_id)

        item = WishlistItem.objects.create(
            name=data.get("name"),
            description=data.get("description", ""),
            collection_type=data.get("collection_type",""),
            notes=data.get("notes",""),
            price_target=data.get("price_target",0),
            link=data.get("link",""),
            owner=user
        )

        return JsonResponse({
            "message": "Item added to wishlist.",
            "item_id": item.id,
            "name": item.name,
            "collection_type" : item.collection_type
        }, status=201)
    
    elif request.method == "GET":
        items = WishlistItem.objects.all()

        return JsonResponse({
            "wishlist": [
                {
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "collection_type" : item.collection_type,
                    "notes": item.notes,
                    "price_target": item.price_target,
                    "link": item.link,
                }
                for item in items
            ]
        })


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

        clerk_user_id = data.get("clerk_user_id")

        if not clerk_user_id:
            return JsonResponse({"Error" : "Missing authentication (clerk id)"}, status=400)

        user = get_or_create_user(clerk_user_id)

        if "name" not in data:
            return JsonResponse({"Error" : "Collection must have a name"}, status=400)

        collection = Collection.objects.create(
            owner=user,
            name=data["name"],
            description=data.get("description",""),
            category=data.get("category", ""),
            collection_type=data.get("type"),
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

        # Clean up data
        purchase_date = data.get("purchase_date")
        if not purchase_date: # Handle empty string or None
            purchase_date = None

        item = Item.objects.create(
            collection=collection,
            name=data["name"],
            description=data.get("description", ""),
            category=data.get("category", ""),
            condition=data.get("condition", "good"),
            quantity=data.get("quantity", 1),
            barcode=data.get("barcode", ""),
            image_url=data.get("image_url", ""),
            purchase_price=data.get("purchase_price") or 0,
            current_value=data.get("current_value") or 0,
            purchase_date=purchase_date,
            usage_status=data.get("usage_status", "stored"),
            listing_status=data.get("listing_status", "not_for_sale"),
            asking_price=data.get("asking_price") or 0,
            is_special_edition=data.get("is_special_edition", False),
            edition_details=data.get("edition_details", ""),
        )

        # Create the type-specific record based on the collection's type
        type_data = {}
        config = COLLECTION_TYPE_CONFIG.get(collection.collection_type)
        if config:
            type_fields = {}
            for field in config["fields"]:
                if field in data:
                    type_fields[field] = data[field]
            type_obj = config["model"].objects.create(item=item, **type_fields)
            type_data = {field: getattr(type_obj, field) for field in config["fields"]}

	# Auto-snapshot: update today's value for this collection
        today = date.today()
        total = collection.items.aggregate(total=Sum("current_value"))["total"] or 0
        ValueSnapshot.objects.update_or_create(
            collection=collection,
            date=today,
            defaults={"total_value": total}
        )

        return JsonResponse({
            "message": "Item added successfully",
            "item": {
                "id": item.id,
                "collection_id": item.collection.id,
                "collection_type": collection.collection_type,
                "name": item.name,
                "description": item.description,
                "category": item.category,
                "condition": item.condition,
                "quantity": item.quantity,
                "barcode": item.barcode,
                "image_url": item.image_url,
                "purchase_price": str(item.purchase_price),
                "current_value": str(item.current_value),
                "purchase_date": str(item.purchase_date) if item.purchase_date else None,
                "usage_status": item.usage_status,
                "listing_status": item.listing_status,
                "asking_price": str(item.asking_price),
                "is_special_edition": item.is_special_edition,
                "edition_details": item.edition_details,
                "created_at": item.created_at.isoformat(),
                "type_attributes": type_data,
            }
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def get_items(request, collection_id):
    try:
        collection = Collection.objects.get(id=collection_id)
        items = collection.items.all()

        items_list = []
        config = COLLECTION_TYPE_CONFIG.get(collection.collection_type)

        for item in items:
            item_data = {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "category": item.category,
                "condition": item.condition,
                "quantity": item.quantity,
                "barcode": item.barcode,
                "image_url": item.image_url,
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

            # Add type-specific fields if they exist
            if config:
                related_name = config["model"].__name__.lower()
                try:
                    type_obj = config["model"].objects.get(item=item)
                    item_data["type_attributes"] = {
                        field: getattr(type_obj, field) for field in config["fields"]
                    }
                except config["model"].DoesNotExist:
                    item_data["type_attributes"] = {}

            items_list.append(item_data)

        return JsonResponse(items_list, safe=False, status=200)

    except Collection.DoesNotExist:
        return JsonResponse({"error": "Collection not found"}, status=404)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_collection(request, collection_id):
    try:
        collection = Collection.objects.get(collection_id=collection_id)
        collection_name = collection.name
        collection.delete()
        return JsonResponse({"Message": f"This collection {collection_name} was deleted successfully"}, status=404)
    
    except Collection.DoesNotExist:
        return JsonResponse({"Error: This collection does not exist"}, status=404)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_item(request, collection_id, item_id):
    try:
        item = Item.objects.get(id=item_id, collection_id=collection_id)
        item_name = item.name
        collection = item.collection
        item.delete()
        
        today = date.today()
        total = collection.items.aggregate(total=Sum("current_value"))["total"] or 0
        ValueSnapshot.objects.update_or_create(
            collection=collection,
            date=today,
            defaults={"total_value": total}
        )
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

    sort = request.GET.get("sort")

    filter_field = request.GET.get("filter")

    filter_value = request.GET.get("value")

    item_type = request.GET.get("type")

    GENERAL_FILTER_FIELDS = {
        "name" : "name__icontains",
        "category" : "category__iexact",
        "usage_status" : "usage_status__iexact",
    }

    VIDEO_GAMES_FILTER_FIELDS = {
        "playStatus" : "play_status__iexact",
        "platform" : "platform__iexact",
        "genre" : "genre__iexact",
        "completeness" : "completeness__iexact",
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
        "completeness" : "completeness__iexact"
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
        "video_games" : VIDEO_GAMES_FILTER_FIELDS,
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

    if filter_field and filter_value:
        filter_by = GENERAL_FILTER_FIELDS.get(filter_field)

        if filter_by is None and item_type:
            type_filters = FILTER_ITEM_TYPES.get(item_type)

            if type_filters:
                filter_by = filter_type.get(filter_val)

        if filter_by is None:
            return JsonResponse({"Error" : "Not a valid filter option"}, status=404)
        data = Item.objects.filter(**{filter_by : filter_value})

    return JsonResponse(list(data.values()), safe=False, status=200)



BARCODE_TYPES = {
        i for i in COLLECTION_TYPE_CONFIG.keys()
        if i not in ["trading_cards", "sports_cards"]
}


def map_fields(item_type, item):
    if item_type == "movies":
        title = item.get("title","")
        format_ = None
        title_lower = title.lower()
        clean_title = None
     
        if "4k" in title_lower or "uhd" in title_lower:
            format_ = "4K UHD"


        elif "blu-ray" in title_lower or "blu ray" in title_lower:
            format_ = "Blu-ray"
           
                
        elif "dvd" in title_lower:
            format_ = "DVD"
          
        
        elif "vhs" in title_lower:
            format_ = "VHS"
      
        if format_:
            match = re.search(r"\(", title)
            if match:
                clean_title = title[:match.start()].strip()

        return {
            "title": clean_title if clean_title else title,
            "genre": None,
            "format": format_,
            "director": None,
            "watched_status": None,
        }

    elif item_type == "music":
        return {
            "album_title": item.get("title"),
            "artist": None,
            "genre": None,
            "format": None,
        }

    elif item_type == "video_games":
        title = item.get("title", "")
        title_lower = title.lower()
        clean_title = None
        platform = None

        if "nintendo switch 2" in title_lower:
            platform = "Nintendo Switch 2"
            idx = title_lower.find("nintendo switch 2")
            clean_title = title[:idx].strip()
            clean_title = re.sub(r"[-(/]", "", clean_title)

        elif "nintendo switch" in title_lower:
            platform = "Nintendo Switch"
            idx = title_lower.find("nintendo switch")
            clean_title = title[:idx].strip()
            clean_title = re.sub(r"[-(/]", "", clean_title)

        elif "ps5" in title_lower or "ps 5" in title_lower or "playstation 5" in title_lower or "play station 5" in title_lower:
            platform = "PS5"
            matches = ["ps5", "PS5", "playstation 5", "play station 5", "PlayStation 5", "PlayStation"]

            for match in matches:
                idx = title_lower.find(match)
                clean_title = title[:idx].strip()
                clean_title = re.sub(r"[-(/]", "", clean_title)
                break
            
        
        elif "ps4" in title_lower or "ps 4" in title_lower or "playstation 4" in title_lower or "play station 4" in title_lower:
            platform = "PS4"
            matches = ["ps4", "PS4", "playstation 4", "play station 4", "PlayStation 4", "PlayStation"]

            for match in matches:
                idx = title_lower.find(match)
                clean_title = title[:idx].strip()
                clean_title = re.sub(r"[-(/]", "", clean_title)
                break
        
        elif "ps3" in title_lower or "ps 3" in title_lower or "playstation 3" in title_lower or "play station 3" in title_lower:
            platform = "PS3"
            matches = ["ps3", "PS3", "playstation 3", "play station 3", "PlayStation 3", "PlayStation"]

            for match in matches:
                idx = title_lower.find(match)
                clean_title = title[:idx].strip()
                clean_title = re.sub(r"[-(/]", "", clean_title)
                break
        
        elif "xbox series x" in title_lower:
            platform = "Xbox Series X"
            idx = title_lower.find("xbox series x")
            clean_title = title[:idx].strip()
            clean_title = re.sub(r"[-(/]", "", clean_title)
        
        elif "xbox one" in title_lower:
            platform = "Xbox One"
            idx = title_lower.find("xbox one")
            clean_title = title[:idx].strip()  
            clean_title = re.sub(r"[-(/]", "", clean_title)      
        
        elif "xbox 360" in title_lower:
            platform = "Xbox 360"
            idx = title_lower.find("xbox 360")
            clean_title = title[:idx].strip()
            clean_title = re.sub(r"[-(/]", "", clean_title)
        
        elif "nintendo 64" in title_lower:
            platform = "Nintendo 64"
            idx = title_lower.find("nintendo 64")
            clean_title = title[:idx].strip()
            clean_title = re.sub(r"[-(/]", "", clean_title)
        
        elif "game boy advance" in title_lower or "gameboy advance" in title_lower:
            platform = "GameBoy Advance"
            matches = ["game boy advance", "gameboy advance"]

            for match in matches:
                idx = title_lower.find(match)
                clean_title = title[:idx].strip()
                clean_title = re.sub(r"[-(/]", "", clean_title)
                break
        
        elif "game boy" in title_lower or "gameboy" in title_lower:
            platform = "GameBoy"
            matches = ["game boy", "gameboy"]

            for match in matches:
                idx = title_lower.find(match)
                clean_title = title[:idx].strip()
                clean_title = re.sub(r"[-(/]", "", clean_title)
                break
        
        elif "nintendo ds" in title_lower:
            platform = "Nintendo DS"
            idx = title_lower.find("nintendo ds")
            clean_title = title[:idx].strip()
            clean_title = re.sub(r"[-(/]", "", clean_title)
        
        elif "ninentdo 3ds" in title_lower:
            platform = "Nintendo 3DS"
            idx = title_lower.find("nintendo 3ds")
            clean_title = title[:idx].strip()
            clean_title = re.sub(r"[-(/]", "", clean_title)
        
        elif "wii u" in title_lower:
            platform = "Wii U"
            idx = title_lower.find("wii u")
            clean_title = title[:idx].strip()
            clean_title = re.sub(r"[-(/]", "", clean_title)

        elif "wii" in title_lower:
            platform = "Wii"
            idx = title_lower.find("wii")
            clean_title = title[:idx].strip()
            clean_title = re.sub(r"[-(/]", "", clean_title)
        
        elif "sega" in title_lower:
            platform = "Sega Genesis"
            idx = title_lower.find("sega")
            clean_title = title[:idx].strip()
            clean_title = re.sub(r"[-(/]", "", clean_title)
        
        elif "atari" in title_lower:
            platform = "Atari 2600"
            idx = title_lower.find("atari")
            clean_title = title[:idx].strip()
            clean_title = re.sub(r"[-(/]", "", clean_title)
        
        else:
             platform = "Other"

        return {
            "title" : clean_title if clean_title else title,
            "platform": platform,
            "genre": None,
            "completeness": None,
            "play_status": None,
        }

    elif item_type == "lego_sets":
        series_type = item.get("brand").lower()
        title = item.get("title", "")
        title_lower = title.lower()

        clean_title = title_lower.replace("lego", "")
        series = None

        if "star wars" in series_type or "star wars" in title_lower:
            series_type = "Star Wars"
        
        elif "technic" in series_type or "technic" in title_lower:
            series_type = "Technic"

        elif "city" in series_type or "city" in title_lower:
            series_type = "City"

        elif "creator" in series_type or "creator" in title_lower:
            series_type = "Creator"
        
        elif "harry potter" in series_type or "harry potter" in title_lower:
            series_type = "Creator"
        
        elif "marvel" in series_type or "marvel" in title_lower:
            series_type = "Creator"

        elif "architecture" in series_type or "creator" in title_lower:
            series_type = "Creator"

        elif "icons" in series_type or "icons" in title_lower:
            series_type = "Creator"

        else:
            series_type = "Other"

        set_number = None
        if item.get("model"):
            set_number = item.get("model")
            if len(set_number) > 6:
                set_number = None
        else:
            match_set_number = re.search(r"\b\d{4,6}\b", title_lower)
            if match_set_number:
                set_number = match_set_number.group(0)
        
        if set_number:
            clean_title = clean_title.replace(set_number, "").strip()

        return {
            "title": clean_title.title(),
            "series": series_type,
            "set_number": set_number,
            "piece_count": None,
            "completeness": None,
        }

    elif item_type == "funko_pops":
        title = item.get("title", "")
        title_lower = title.lower()
        series_type = None
        clean_title = title_lower.replace("funko","").replace("pop","")

        if "tv" in title_lower:
            series_type = "TV"
            clean_title = clean_title[:clean_title.find("tv")]
            lean_title = re.sub(r"[-(/!]", "", clean_title)
            clean_title = " ".join(clean_title.split())

        elif "movie" in title_lower or "movies" in title_lower:
            series_type = "Movies"
            if "movie" in title_lower:
                clean_title = clean_title[:clean_title.find("movie")]
            elif "movies" in title_lower:
                clean_title = clean_title[:clean_title.find("movies")]
            
            clean_title = re.sub(r"[-(/!]", "", clean_title)
            clean_title = " ".join(clean_title.split())
        
        elif "game" in title_lower or "games" in title_lower:
            series_type = "Games"
            if "game" in title_lower:
                clean_title = clean_title[:clean_title.find("game")]
            elif "game" in title_lower:
                clean_title = clean_title[:clean_title.find("games")]
            
            clean_title = re.sub(r"[-(/!]", "", clean_title)
            clean_title = " ".join(clean_title.split())
        
        elif "marvel" in title_lower:
            series_type = "Marvel"
            clean_title = clean_title[:clean_title.find("marvel")]
            clean_title = re.sub(r"[-(/!]", "", clean_title)
            clean_title = " ".join(clean_title.split())
        
        elif "dc" in title_lower:
            series_type = "DC"
            clean_title = clean_title[:clean_title.find("dc")]
            clean_title = re.sub(r"[-(/!]", "", clean_title)
            clean_title = " ".join(clean_title.split())
        
        elif "disney" in title_lower:
            series_type = "Disney"
            clean_title = clean_title[:clean_title.find("disney")]
            clean_title = re.sub(r"[-(/!]", "", clean_title)
            clean_title = " ".join(clean_title.split())
        
        elif "star wars" in title_lower:
            series_type = "Star Wars"
            clean_title = clean_title[:clean_title.find("star wars")]
            clean_title = re.sub(r"[-(/!]", "", clean_title)
            clean_title = " ".join(clean_title.split())
        
        elif "anime" in title_lower or "animation" in title_lower:
            series_type = "Anime"
            if "anime" in title_lower:
                clean_title = clean_title[:clean_title.find("anime")]
            elif "animation" in title_lower:
                clean_title = clean_title[:clean_title.find("animation")]
            
            clean_title = re.sub(r"[-(/!]", "", clean_title)
            clean_title = " ".join(clean_title.split())
                   
        else:
            series_type = "Other"

        return {
            "title" : clean_title.title(),
            "series": series_type,
            "box_number": item.get("model"),
            "exclusive": None,
            "completeness": None,
        }

    elif item_type in ["comics", "books"]:
        title = item.get("title")
        title_lower = title.lower()
        clean_title = title_lower
        publisher = None

        if "marvel" in title_lower:
            publisher = "Marvel"            

        elif "dc" in title_lower:
            publisher = "DC" 
       
        elif "image" in title_lower:
            publisher = "Image"

        elif "dark horse" in title_lower:
            publisher = "Dark Horse"

        elif "idw" in title_lower:
            publisher = "IDW"
\
        elif "boom" in title_lower:
            publisher = "Boom! Studios"

        else:
            publisher = "Other"    

        find_issue = re.search(r"#(\d+)", clean_title)
        issue_number = None
        if find_issue:
            issue_number = find_issue.group(1)

        return {
            "title": clean_title.title(),
            "publisher": publisher,
            "issue_title": clean_title.title(),
            "issue_number": issue_number,
            "grade": None,
            "read_status": None,
        }

    return {}

GENRES = {
    "hip hop": "Hip-Hop",
    "hip-hop": "Hip-Hop",
    "rap": "Hip-Hop",
    "hiphop": "Hip-Hop",

    "country": "Country",

    "pop": "Pop",

    "rock": "Rock",

    "jazz": "Jazz",

    "funk": "R&B",
    "soul": "R&B",
    "r&b": "R&B",
    "rnb": "R&B",
    "rhythm and blues": "R&B",
    "blues": "R&B",
    "r and b": "R&B",

    "electronic": "Electronic",
    "edm": "Electronic",
    
    "metal": "Metal",
    "heavy metal": "Metal",
}

FORMATS = {
    "cd": "CD",
    "cdr": "CD",

    "vinyl": "Vinyl",
    "lp": "Vinyl",

    "cassette": "Cassette",

    "digital": "Digital",

    "8-track": "8-track",
}

def musicbrainz_api(barcode):
    url = f"https://musicbrainz.org/ws/2/release/?query=barcode:{barcode}&fmt=json"

    headers = {
        "User-Agent": "HoardHero"
    }

    r = requests.get(url, headers=headers, timeout=10)
    data = r.json()

    releases = data.get("releases", [])
    if not releases:
        return None

    release = releases[0]

    title = release.get("title")

    artist = None
    artist_info = release.get("artist-credit", [])
    if artist_info:
        artist_list = artist_info[0]
        artist = artist_list.get("name")
      
    return ({
        "title" : title,
        "artist" : artist,
    })


def discogs_api(barcode):
    url = f"https://api.discogs.com/database/search?barcode={barcode}"

    headers = {
        "User-Agent": "HoardHero"
    }

    r = requests.get(url, headers=headers, timeout=10)
    data = r.json()

    results = data.get("results", [])
    if not results:
        return None

    item = results[0]

    release_id = item.get("id")

    if not release_id:
        return None
    
    release_url = f"https://api.discogs.com/releases/{release_id}"
    r2 = requests.get(release_url, headers=headers, timeout=10)
    release_data = r2.json()

    images = release_data.get("images", [])
    image_url = images[0]["uri"] if images else None

    
    market_url = f"https://api.discogs.com/marketplace/stats/{release_id}"
    r3 = requests.get(market_url, headers=headers, timeout=10)
    market_data = r3.json()
    market_value = None
    if market_data.get("num_for_sale", 0) > 0:
        market_value = market_data.get("lowest_price", {}).get("value")
    
    if market_value is None:
        market_value = market_data.get("median", {}).get("value")
    
    return {
        "genre": item.get("genre", []),
        "format": item.get("format", []),
        "image": image_url,
        "market_value": market_value
    }

def match_keyword(value, keywords):
    if not value:
        return None

    v = value.lower()

    for keyword, result in keywords.items():
        if keyword in v:
            return result

    return "Other"

@csrf_exempt
@require_http_methods(["POST"])
def barcode(request):
    image_file = request.FILES.get("image") #gets the barcode image from HoardHero

    if not image_file:
        return JsonResponse({"error": "nothing uploaded"}, status=400)
    
    try:
        image = Image.open(image_file) #gets the data from the image file uploaded to hoard hero
    except UnidentifiedImageError:
        return JsonResponse({"error": "Invalid file type"}, status=400)

    decoded_code = decode(image)

    if not decoded_code:
        return JsonResponse({"error": "no barcode found"}, status=400)

    item_type = request.POST.get("item_type")
    print("🟢 BACKEND RECEIVED ITEM TYPE:", item_type)

    if not item_type or item_type not in BARCODE_TYPES:
        return JsonResponse({"error": "Invalid or missing item_type"}, status=400)
        

    barcode = decoded_code[0].data.decode("utf-8") #decodes barcode
    
    if item_type == "music": #needs specific music api
        musicbrainz = musicbrainz_api(barcode)
        discogs = discogs_api(barcode)

        if not musicbrainz:
            return JsonResponse({"error": "Music not found"}, status=404)

        title = musicbrainz.get("title")
        artist = musicbrainz.get("artist")
      
        genre_list = discogs.get("genre", []) if discogs else []
        format_list = discogs.get("format", []) if discogs else []
        image = discogs.get("image")
        market_value = discogs.get("market_value")

        genre = match_keyword(
            genre_list[0] if genre_list else "",
            GENRES
        )

        format_ = match_keyword(
            format_list[0] if format_list else "",
            FORMATS
        )
      
        result = {
            "name": title,
            "barcode": barcode,
            "image": image,
            "current_value": market_value,
            "fields": {
                "album_title": title,
                "artist": artist,
                "genre": genre,
                "format": format_,
            }
        }

        return JsonResponse(result)


    url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={barcode}"
   
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return JsonResponse({"error": "Failed to fetch item"}, status=500)
    

    if data.get("code") != "OK" or data.get("total", 0) == 0:
        return JsonResponse({"error": "Item not found"}, status=404)
    
    items = data.get("items", [])
    if not items:
        return JsonResponse({"error": "Corrupted data"}, status=404)
    
    item = items[0]

    fields = COLLECTION_TYPE_CONFIG[item_type]["fields"]

    filtered_item = {field: item.get(field) for field in fields}

    upc_image = item.get("images", [None])[0]

    market_price = item.get("highest_recorded_price")

    result = {
        "name": item.get("title"),
        "description": item.get("description"),
        "barcode": barcode,
        "fields": map_fields(item_type, item),
        "image": upc_image,
        "current_value": market_price
    }

    return JsonResponse(result)

@csrf_exempt
@require_http_methods(["PATCH"])
def move_wishlist_item_to_collection(request, item_id, collection_id):
    print("FROM MOVE ITEM ID: ", item_id)

    wishlist_item = WishlistItem.objects.filter(id=item_id).first()

    if not wishlist_item:
        return JsonResponse({"Error" : "This item cannot be found"}, status=404)
    
    collection = Collection.objects.filter(id=collection_id).first()

    if not collection_id:
        return JsonResponse({"Error" : "Collection cannot be found"}, status=404)
    
    item = Item.objects.create(
        collection=collection, 
        title=wishlist_item.name, 
        description=wishlist_item.description
        )

    if collection.type == "video_games":
        VideoGameItem.objects.create(item=item)
    
    elif collection_type == "trading_cards":
        TradingCardItem.objects.create(item=item)
    
    elif collection_type == "comics":
        ComicItem.objects.create(item=item)
    
    elif collection_type == "funko_pops":
        FunkoPopItem.objects.create(item=item)

    elif collection_type == "lego_sets":
        LegoSetItem.objects.create(item=item)
    
    elif collection_type == "sports_cards":
        SportsCardItem.objects.create(item=item)
    
    elif collection_type == "music":
        MusicItem.objects.create(item=item)
    
    elif collection_type == "movies":
        MovieItem.objects.create(item=item)

    delete_wishlist_item(request, item_id)

    return JsonResponse({"Message" : "Wishlist item moved successfully"})
    

@csrf_exempt
@require_http_methods(["GET"])
def get_wishlist(request):
    items = WishlistItem.objects.all()
    data = [{
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "collection_type": item.collection_type,
        "notes": item.notes,
        "price_target": str(item.price_target),
        "link": item.link,
    } for item in items]
    return JsonResponse(data, safe=False)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_wishlist_item(request, item_id):
    try:
        item = WishlistItem.objects.get(id=item_id)
        item.delete()
        return JsonResponse({"message": "Wishlist item deleted"}, status=200)
    except WishlistItem.DoesNotExist:
        return JsonResponse({"error": "Wishlist item not found"}, status=404)

@require_http_methods(["GET"])
def value_history(request, collection_id):
    try:
        collection = Collection.objects.get(id=collection_id)
    except Collection.DoesNotExist:
        return JsonResponse({"error": "Collection not found"}, status=404)

    days = int(request.GET.get("days", 30))
    if days not in [30, 60]:
        return JsonResponse({"error": "days must be 30 or 60"}, status=400)

    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    snapshots = ValueSnapshot.objects.filter(
        collection=collection,
        date__gte=start_date,
        date__lte=end_date
    ).order_by("date")

    data = []
    for snap in snapshots:
        data.append({
            "date": snap.date.isoformat(),
            "total_value": str(snap.total_value),
        })

    if not data:
        current_total = collection.items.aggregate(
            total=Sum("current_value")
        )["total"] or 0
        data.append({
            "date": end_date.isoformat(),
            "total_value": str(current_total),
        })

    return JsonResponse({
        "collection_id": collection_id,
        "collection_name": collection.name,
        "days": days,
        "history": data,
    }, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def record_value_snapshot(request):
    try:
        today = date.today()
        collections = Collection.objects.all()
        recorded = 0

        for collection in collections:
            total = collection.items.aggregate(
                total=Sum("current_value")
            )["total"] or 0

            ValueSnapshot.objects.update_or_create(
                collection=collection,
                date=today,
                defaults={"total_value": total}
            )
            recorded += 1

        return JsonResponse({
            "message": f"Recorded snapshots for {recorded} collections",
            "date": today.isoformat()
        }, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

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

@csrf_exempt
@require_http_methods(["GET"])
def ebay_search(request):
    query = request.GET.get("q")

    if not query:
        return JsonResponse({"error": "Missing search query"}, status=400)

    try:
        ebay = Ebay_API()

        raw_data = ebay.fetch_items(query)

        parsed_data = ebay.parse_items(raw_data)
        return JsonResponse({
            "query": query,
            "raw_data": raw_data,
            "results": parsed_data
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)  