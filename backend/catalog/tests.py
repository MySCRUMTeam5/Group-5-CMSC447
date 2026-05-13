from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model
from .models import Collection, Item
from .views import sort_filter_collection, add_item_to_wishlist, delete_item_from_wishlist
from datetime import date
import json
from catalog.models import TradingCardItem, DuplicateFlag

User = get_user_model()

class duplicateBug(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass123")

        self.poke_coll = Collection.objects.create(collection_type="trading_cards",name="Pokemon", owner=self.user)
        self.charizard_item = Item.objects.create(collection=None, name="Charizard")
        self.charizard_card = TradingCardItem.objects.create(item=self.charizard_item)

        self.dup_charizard_item = Item.objects.create(collection=None, name="Charizard")
        self.dup_charizard_card = TradingCardItem.objects.create(item=self.dup_charizard_item)
    
    def test_bug_fix_edit_dup(self):
        DuplicateFlag.objects.create(
            collection=self.poke_coll, 
            item_a=self.charizard_item, 
            item_b=self.dup_charizard_item, 
            is_confirmed_duplicate=True
            )

        self.dup_charizard_item.name = "Charizard V2"
        self.dup_charizard_item.save()

        self.assertEqual(self.dup_charizard_item.name, "Charizard V2")

class WishlistNormal(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass123")

        self.charizard = Item.objects.create(collection=None, name="Charizard", status=Item.ItemStatus.WISHLIST)
        self.pikachu = Item.objects.create(collection=None, name="Pikachu", status=Item.ItemStatus.WISHLIST)
        self.squirtle = Item.objects.create(collection=None, name="Squirtle", status=Item.ItemStatus.WISHLIST)

    def test_get_wishlist_item(self):
        request = self.factory.get("/wishlist/items")
        response = add_item_to_wishlist(request)
        data = json.loads(response.content)

        self.assertEqual(len(data["wishlist"]), 3)

    def test_delete_wishlist_item(self):
        charizard_id = self.charizard.id

        request = self.factory.delete(f"wishlist/delete/{charizard_id}")

        response = delete_item_from_wishlist(request, charizard_id)

        self.assertEqual(response.status_code, 200)

        self.assertFalse(Item.objects.filter(id=charizard_id).exists())

        request2 = self.factory.get("/wishlist/items/")
        
        response2 = add_item_to_wishlist(request2)

        data2 = json.loads(response2.content)

        self.assertEqual(len(data2["wishlist"]), 2)


class TestFilterNormal(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.collection = Collection.objects.create(collection_type="video_games",name="Pokemon", owner=self.user)

        fire_red = Item.objects.create(collection=self.collection, name="Fire Red", usage_status=Item.UsageStatus.STORED)
        silver = Item.objects.create(collection=self.collection, name="Silver", usage_status=Item.UsageStatus.IN_USE)
        crystal = Item.objects.create(collection=self.collection, name="Crystal", usage_status=Item.UsageStatus.NOT_USED)
        gold = Item.objects.create(collection=self.collection, name="Gold", usage_status=Item.UsageStatus.STORED)
        leaf_green = Item.objects.create(collection=self.collection, name="Leaf Green", usage_status=Item.UsageStatus.IN_USE)
        yellow = Item.objects.create(collection=self.collection, name="Yellow", usage_status=Item.UsageStatus.NOT_USED)

    def test_filter_red(self):
        request = self.factory.get("/items/?filter=name&value=red")
        response = sort_filter_collection(request)
        data = json.loads(response.content)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Fire Red")

    def test_filter_e(self):
        request = self.factory.get("/items/?filter=name&value=e")
        response = sort_filter_collection(request)
        data = json.loads(response.content)

        self.assertEqual(len(data), 4)
        self.assertEqual(data[0]["name"], "Yellow")
        self.assertEqual(data[1]["name"], "Leaf Green")
        self.assertEqual(data[2]["name"], "Silver")
        self.assertEqual(data[3]["name"], "Fire Red")

    def test_filter_stored(self):
        request = self.factory.get("items/?filter=usage_status&value=stored")
        response = sort_filter_collection(request)
        data = json.loads(response.content)

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "Gold")
        self.assertEqual(data[1]["name"], "Fire Red")

    def test_filter_in_use(self):
        request = self.factory.get("items/?filter=usage_status&value=in_use")
        response = sort_filter_collection(request)
        data = json.loads(response.content)

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "Leaf Green")
        self.assertEqual(data[1]["name"], "Silver")
    
    def test_filter_not_used(self):
        request = self.factory.get("items/?filter=usage_status&value=not_used")
        response = sort_filter_collection(request)
        data = json.loads(response.content)

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "Yellow")
        self.assertEqual(data[1]["name"], "Crystal")

class TestSortEmptyColl(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.collection = Collection.objects.create(collection_type="video_games",name="Pokemon", owner=self.user)

    def test_sort_a_z_empty(self):
        request = self.factory.get("/items/?sort=alpha_ascend")
        response = sort_filter_collection(request)
        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_sort_z_a_empty(self):
        request = self.factory.get("/items/?sort=alpha_descend")
        response = sort_filter_collection(request)
        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_sort_date_ascend_empty(self):
        request = self.factory.get("/items/?sort=date_ascend")
        response = sort_filter_collection(request)
        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_sort_date_descend_empty(self):
        request = self.factory.get("/items/?sort=date_descend")
        response = sort_filter_collection(request)
        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_sort_price_ascend_empty(self):
        request = self.factory.get("/items/?sort=p_price_ascend")
        response = sort_filter_collection(request)
        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_sort_price_descend_empty(self):
        request = self.factory.get("/items/?sort=p_price_descend")
        response = sort_filter_collection(request)
        data = json.loads(response.content)
        self.assertEqual(data, [])


class TestSortNoColl(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_sort_a_z_no_coll(self):
        request = self.factory.get("/items/?sort=alpha_ascend")
        response = sort_filter_collection(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_sort_z_a_no_coll(self):
        request = self.factory.get("/items/?sort=alpha_descend")
        response = sort_filter_collection(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_sort_date_ascend_no_coll(self):
        request = self.factory.get("/items/?sort=date_ascend")
        response = sort_filter_collection(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_sort_date_descend_no_coll(self):
        request = self.factory.get("/items/?sort=date_descend")
        response = sort_filter_collection(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_sort_price_ascend_no_coll(self):
        request = self.factory.get("/items/?sort=p_price_ascend")
        response = sort_filter_collection(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_sort_price_descend_no_coll(self):
        request = self.factory.get("/items/?sort=p_price_descend")
        response = sort_filter_collection(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, [])


class TestSortPriceNormal(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.collection = Collection.objects.create(collection_type="video_games",name="Pokemon", owner=self.user)

        Item.objects.create(collection=self.collection, name="Fire Red", purchase_price=19.99)
        Item.objects.create(collection=self.collection, name="Silver", purchase_price=9.99)
        Item.objects.create(collection=self.collection, name="Crystal", purchase_price=30)
        Item.objects.create(collection=self.collection, name="Gold", purchase_price=45.87)
        Item.objects.create(collection=self.collection, name="Leaf Green", purchase_price=72.89)

    def test_sort_price_ascend(self):
        request = self.factory.get("/items/?sort=p_price_ascend")
        response = sort_filter_collection(request)
        data = json.loads(response.content)
        expected_order = ["Silver", "Fire Red", "Crystal", "Gold", "Leaf Green"]
        actual_order = [item["name"] for item in data]
        self.assertEqual(actual_order, expected_order)

    def test_sort_price_descend(self):
        request = self.factory.get("/items/?sort=p_price_descend")
        response = sort_filter_collection(request)
        data = json.loads(response.content)
        expected_order = ["Leaf Green", "Gold", "Crystal", "Fire Red", "Silver"]
        actual_order = [item["name"] for item in data]
        self.assertEqual(actual_order, expected_order)


class TestSortAlphaNormal(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.collection = Collection.objects.create(collection_type="video_games",name="Pokemon", owner=self.user)

        Item.objects.create(collection=self.collection, name="Fire Red")
        Item.objects.create(collection=self.collection, name="Silver")
        Item.objects.create(collection=self.collection, name="Crystal")
        Item.objects.create(collection=self.collection, name="Gold")
        Item.objects.create(collection=self.collection, name="Leaf Green")

    def test_sort_a_z_normal(self):
        request = self.factory.get("/items/?sort=alpha_ascend")
        response = sort_filter_collection(request)
        data = json.loads(response.content)
        expected_order = ["Crystal", "Fire Red", "Gold", "Leaf Green", "Silver"]
        actual_order = [item["name"] for item in data]
        self.assertEqual(actual_order, expected_order)

    def test_sort_z_a_normal(self):
        request = self.factory.get("/items/?sort=alpha_descend")
        response = sort_filter_collection(request)
        data = json.loads(response.content)
        expected_order = ["Silver", "Leaf Green", "Gold", "Fire Red", "Crystal"]
        actual_order = [item["name"] for item in data]
        self.assertEqual(actual_order, expected_order)


class TestSortDateNormal(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.collection = Collection.objects.create(collection_type="video_games",name="Pokemon", owner=self.user)

        Item.objects.create(collection=self.collection, name="Fire Red", purchase_date=date(2025, 8, 10))
        Item.objects.create(collection=self.collection, name="Silver", purchase_date=date(2025, 7, 10))
        Item.objects.create(collection=self.collection, name="Crystal", purchase_date=date(2026, 3, 10))
        Item.objects.create(collection=self.collection, name="Gold", purchase_date=date(2024, 8, 10))
        Item.objects.create(collection=self.collection, name="Leaf Green", purchase_date=date(2026, 3, 16))

    def test_sort_date_ascend_normal(self):
        request = self.factory.get("/items/?sort=date_ascend")
        response = sort_filter_collection(request)
        data = json.loads(response.content)
        expected_order = ["Gold", "Silver", "Fire Red", "Crystal", "Leaf Green"]
        actual_order = [item["name"] for item in data]
        self.assertEqual(actual_order, expected_order)

    def test_sort_date_descend_normal(self):
        request = self.factory.get("/items/?sort=date_descend")
        response = sort_filter_collection(request)
        data = json.loads(response.content)
        expected_order = ["Leaf Green", "Crystal", "Fire Red", "Silver", "Gold"]
        actual_order = [item["name"] for item in data]
        self.assertEqual(actual_order, expected_order)


class DeleteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="Test", password="testpass123")
        self.collection = Collection.objects.create(name="Delete Test Collection", owner=self.user)
        self.item = Item.objects.create(name="Item to delete", collection=self.collection)

    def test_delete_item_sucsess(self):
        self.assertTrue(Item.objects.filter(id=self.item.id).exists())
        url = f"/api/items/delete/{self.collection.id}/{self.item.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Item.objects.filter(id=self.item.id).exists())

    def test_delete_item_not_exsist(self):
        self.assertTrue(Item.objects.filter(id=self.item.id).exists())

        collectionId = self.collection.id
        itemId = self.item.id

        url = f"/api/items/delete/{collectionId}/{itemId}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Item.objects.filter(id=self.item.id).exists())

        url = f"/api/items/delete/{collectionId}/{itemId}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)


class AddItemTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.collection = Collection.objects.create(owner=self.user, name="Pokemon Cards")

    def test_cant_add_empty_item(self):
        response = self.client.post(
            "/api/items/add/",
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_cant_add_without_collection_id(self):
        response = self.client.post(
            "/api/items/add/",
            data=json.dumps({
                "name": "Charizard"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_cant_add_without_name(self):
        response = self.client.post(
            "/api/items/add/",
            data=json.dumps({
                "collection_id": self.collection.id
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_cant_add_without_collection_id_and_name(self):
        response = self.client.post(
            "/api/items/add/",
            data=json.dumps({
                "category": "cards"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_add_item_success(self):
        response = self.client.post(
            "/api/items/add/",
            data=json.dumps({
                "collection_id": self.collection.id,
                "name": "Charizard",
                "category": "Pokemon Cards",
                "condition": "mint",
                "purchase_price": 350.00
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Item.objects.count(), 1)
        self.assertEqual(Item.objects.first().name, "Charizard")


class CollectionItemCountTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        self.collection = Collection.objects.create(
            owner=self.user,
            name="Video Games",
            description="Test collection",
            category="games"
        )

    def test_add_one_item_increments_count_by_one(self):
        response = self.client.post(
            "/api/items/add/",
            data=json.dumps({
                "collection_id": self.collection.id,
                "name": "Zelda",
                "quantity": 1
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        count_response = self.client.get(
            f"/api/collections/{self.collection.id}/item-count/"
        )
        self.assertEqual(count_response.status_code, 200)

        data = count_response.json()
        self.assertEqual(data["total_items"], 1)

    def test_delete_one_item_decrements_count_by_one(self):
        item = Item.objects.create(
            collection=self.collection,
            name="Mario Kart",
            quantity=1
        )

        delete_response = self.client.delete(
            f"/api/items/delete/{self.collection.id}/{item.id}/"
        )
        self.assertEqual(delete_response.status_code, 200)

        count_response = self.client.get(
            f"/api/collections/{self.collection.id}/item-count/"
        )
        self.assertEqual(count_response.status_code, 200)

        data = count_response.json()
        self.assertEqual(data["total_items"], 0)

    def test_add_multiple_items_tracks_correct_total(self):
        self.client.post(
            "/api/items/add/",
            data=json.dumps({
                "collection_id": self.collection.id,
                "name": "Zelda",
                "quantity": 2
            }),
            content_type="application/json"
        )

        self.client.post(
            "/api/items/add/",
            data=json.dumps({
                "collection_id": self.collection.id,
                "name": "Mario Kart",
                "quantity": 3
            }),
            content_type="application/json"
        )

        self.client.post(
            "/api/items/add/",
            data=json.dumps({
                "collection_id": self.collection.id,
                "name": "Metroid",
                "quantity": 1
            }),
            content_type="application/json"
        )

        count_response = self.client.get(
            f"/api/collections/{self.collection.id}/item-count/"
        )
        self.assertEqual(count_response.status_code, 200)

        data = count_response.json()
        self.assertEqual(data["total_items"], 6)

    def test_delete_multiple_items_tracks_correct_total(self):
        item1 = Item.objects.create(
            collection=self.collection,
            name="Zelda",
            quantity=2
        )
        item2 = Item.objects.create(
            collection=self.collection,
            name="Mario Kart",
            quantity=3
        )
        Item.objects.create(
            collection=self.collection,
            name="Metroid",
            quantity=1
        )

        delete_response_1 = self.client.delete(
            f"/api/items/delete/{self.collection.id}/{item1.id}/"
        )
        self.assertEqual(delete_response_1.status_code, 200)

        delete_response_2 = self.client.delete(
            f"/api/items/delete/{self.collection.id}/{item2.id}/"
        )
        self.assertEqual(delete_response_2.status_code, 200)

        count_response = self.client.get(
            f"/api/collections/{self.collection.id}/item-count/"
        )
        self.assertEqual(count_response.status_code, 200)

        data = count_response.json()
        self.assertEqual(data["total_items"], 1)

    def test_empty_collection_returns_zero_items(self):
        count_response = self.client.get(
            f"/api/collections/{self.collection.id}/item-count/"
        )
        self.assertEqual(count_response.status_code, 200)

        data = count_response.json()
        self.assertEqual(data["total_items"], 0)


class addCollection(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")

        Collection.objects.create(collection_type="video_games",name="Pokemon", owner=self.user)

        Collection.objects.create(collection_type="trading_cards",name="Lord of the Rings Set", owner=self.user)

        Collection.objects.create(collection_type="lego_sets",name="Star Wars", owner=self.user)

    def test_add_collection_normal(self):
        self.client.force_login(self.user)

        response_1 = self.client.post("/api/collections/", {"collection_type" : "video_games", "name" : "Pokemon Test"}, content_type="application/json")

        self.assertEqual(response_1.status_code, 201)

        response_2 = self.client.post("/api/collections/", {"collection_type" : "trading_cards", "name" : "Lord of the Rings Set Test"}, content_type="application/json")
        
        self.assertEqual(response_2.status_code, 201)
        
        response_3 = self.client.post("/api/collections/", {"collection_type" : "lego_sets", "name" : "Star Wars Test"}, content_type="application/json")

        self.assertEqual(response_3.status_code, 201)
        
        self.assertTrue(Collection.objects.filter(name="Pokemon").exists())

        self.assertTrue(Collection.objects.filter(name="Lord of the Rings Set").exists())

        self.assertTrue(Collection.objects.filter(name="Star Wars").exists())   

class everything(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")

        pokemon_coll = Collection.objects.create(collection_type="video_games",name="Pokemon", owner=self.user)
        fire_red_item = Item.objects.create(collection=self.collection, name="Fire Red")
        fire_red_game = VideoGameItem.objects.create(item=fire_red_item, platform="Nintendo Switch 2", play_status="Playing")
        silver_item = Item.objects.create(collection=self.collection, name="Silver")
        silver_game = VideoGameItem.objects.create(item=silver_item, platform="Nintendo Switch 2", play_status="Played")
        crystal_item = Item.objects.create(collection=self.collection, name="Crystal")
        crystal_game = VideoGameItem.objects.create(item=crystal_item, platform="Nintendo Switch 2", play_status="Not Played")
        

        lotr_coll = Collection.objects.create(collection_type="trading_cards",name="Lord of the Rings Set", owner=self.user)
        sam_item = Item.objects.create(collection=self.collection, name="Sam, Loyal Attendant")
        sam_card = TradingCardItem.objects.create(item=sam_item, series="Tales of Middle Earth")
        frodo_item = Item.objects.create(collection=self.collection, name="Frodo, Adventurous Hobbit")
        frodo_card = TradingCardItem.objects.create(item=frodo_item, series="Tales of Middle Earth")

        lego_coll = Collection.objects.create(collection_type="lego_sets",name="Star Wars", owner=self.user)
        star_destroyer_item =  Item.objects.create(collection=self.collection, name="Star Destroyer")
        star_destroyer_set = LegoSetItem.objects.create(item=star_destroyer_item, series="Star Wars", completeness="completed", piece_count=630)
        falcon_item =  Item.objects.create(collection=self.collection, name="Millenium Falcon")
        falcon_set = LegoSetItem.objects.create(item=falcon_item, series="Star Wars", completeness="completed", piece_count=7500)
    
    def end_to_end_normal(self):
        self.client.force_login(self.user) #logs user in

        #Post Pokemon Collection and check it posted
        post_pokemon_coll_resp = self.client.post("/api/collections/", {"collection_type" : "video_games", "name" : "Pokemon Test"}, content_type="application/json")
        pok_collection_id = post_pokemon_coll_resp.json()["id"]
        self.assertEqual(post_pokemon_coll_resp, 201) #Gets correct status code after posting
        self.assertTrue(Collection.objects.filter(name="Pokemon").exists()) #Ensures it actually exists in backend
        
        #Post Items in the Pokemon Collection
        post_fire_red_resp = self.client.post("/api/items/add/", {"collection_id" : pok_collection_id, "name" : "Fire Red Test"}, content_type="application/json")
        self.assertEqual(post_fire_red_resp, 201) #Gets correct status code after posting
        self.assertTrue(Item.objects.filter(name="Fire Red").exists()) #Ensures it actually exists in backend
        fire_red_id = post_fire_red_resp.json()["id"]
        post_silver_resp = self.client.post("/api/items/add/", {"collection_id" : pok_collection_id, "name" : "Silver Test"}, content_type="application/json")
        self.assertEqual(post_silver_resp, 201) #Gets correct status code after posting
        self.assertTrue(Collection.objects.filter(name="Silver").exists()) #Ensures it actually exists in backend
        post_crystal_resp = self.client.post("/api/items/add/", {"collection_id" : pok_collection_id, "name" : "Crystal Test"}, content_type="application/json")
        self.assertEqual(post_crystal_resp, 201) #Gets correct status code after posting
        self.assertTrue(Collection.objects.filter(name="Crystal").exists()) #Ensures it actually exists in backend


        #Post LotR MtG Collection
        post_lotr_coll_resp = self.client.post("/api/collections/", {"collection_type" : "trading_cards", "name" : "Lord of the Rings Test"}, content_type="application/json")
        self.assertEqual(post_lotr_coll_resp, 201) #Gets correct status code after posting
        self.assertTrue(Item.objects.filter(name="Lord of the Rings").exists()) #Ensures it actually exists in backend
        lotr_collection_id = post_lotr_coll_resp.json()["id"]

        #Post Items in the LotR MtG Collection
        post_sam_resp = self.client.post("/api/items/add/", {"collection_id" : lotr_collection_id, "name" : "Sam, Loyal Attendant Test"}, content_type="application/json")
        self.assertEqual(post_sam_resp, 201) #Gets correct status code after posting
        self.assertTrue(Item.objects.filter(name="Sam, Loyal Attendant").exists()) #Ensures it actually exists in backend
        post_frodo_resp = self.client.post("/api/items/add/", {"collection_id" : lotr_collection_id, "name" : "Frodo, Adventurous Hobbit Test"}, content_type="application/json")     
        self.assertEqual(post_frodo_resp, 201) #Gets correct status code after posting
        self.assertTrue(Item.objects.filter(name="Frodo, Adventurous Hobbit").exists()) #Ensures it actually exists in backend 

        #Post Star Wars Lego Collection
        post_swlego_coll_resp = self.client.post("/api/collections/", {"collection_type" : "lego_sets", "name" : "Star Wars Legos Test"}, content_type="application/json")
        swlego_collection_id = post_swlego_coll_resp.json()["id"]
        self.assertEqual(post_swlego_coll_resp, 201) #Gets correct status code after posting
        self.assertTrue(Item.objects.filter(name="Star Wars").exists())
        lego_coll_id = post_swlego_coll_resp.json()["id"]

        #Post Items in Star Wars Lego Collection
        post_star_dest_coll_resp = self.client.post("/api/items/add/", {"collection_id" : swlego_collection_id, "name" : "Star Destroyer Test"}, content_type="application/json")
        self.assertEqual(post_star_dest_coll_resp, 201) #Gets correct status code after posting
        self.assertTrue(Item.objects.filter(name="Star Destroyer").exists())
        post_millfal_coll_resp = self.client.post("/api/items/add/", {"collection_id" : swlego_collection_id, "name" : "Millenium Falcon Test"}, content_type="application/json")
        self.assertEqual(post_millfal_coll_resp, 201) #Gets correct status code after posting
        self.assertTrue(Item.objects.filter(name="Millenium Falcon").exists())

        #Create a Duplicate
        duplicate_frodo = Item.objects.create(collection=lotr_collection_id, name="Frodo, Adventurous Hobbit")
        duplicate_frodo_resp = self.client.post("/api/items/add", {"collection_id" : lotr_collection_id, "name" : "Frodo, Adventurous Hobbit"})
        dup_frodo_id = duplicate_frodo_response.json()["id"]

        #Make sure it shows duplicate on front and Backend
        self.assertEqual(duplicate_frodo_resp, 201)
        self.assertTrue(Item.objects.filter(name="Frodo, Adventurous Hobbit").count(), 2)

        #Sort Collection A-Z
        request_1 = self.pokemon_coll.get("/items/?sort=alpha_ascend")
        response_1 = sort_filter_collection(request_1)
        data = json.loads(response_1.content)
        expected_order = ["Crystal", "Fire Red", "Silver"]
        actual_order = [item["name"] for item in data]
        self.assertEqual(actual_order, expected_order)

        #Sort Collection Z-A
        request_2 = self.lotr_coll.get("/items/?sort=alpha_descend")
        response_2 = sort_filter_collection(request_2)
        data = json.loads(response_2.content)
        expected_order = ["Sam, Loyal Attendant", "Frodo, Adventurous Hobbit", "Frodo, Adventurous Hobbit"]
        actual_order = [item["name"] for item in data]
        self.assertEqual(actual_order, expected_order)      

        #Filter Collection by letter
        request_3 = self.lego_coll.get("/items/?filter=name&value=f")
        response_3 = sort_filter_collection(request_3)
        data = json.loads(response_3.content)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Millenium Falcon")

        #Delete an Item
        response_4 = self.client.delete(f"items/delete/{pok_collection_id}/{fire_red_id}/")
        self.assertEqual(response_4, 201) 
        self.assertFalse(Item.objects.filter(name="Fire Red").exists())

        #Delete a Duplicate Item
        response_5 = self.client.delete(f"items/delete/{lotr_collection_id}/{dup_frodo_id}/")
        self.assertEqual(response_5, 201) 
        self.assertTrue(Item.objects.filter(name="Frodo, Adventurous Hobbit").count(), 1)

        #Delete a Collection
        response_6 = self.client.delete(f"collections/delete/{lotr_collection_id}/")
        self.assertEqual(respone_6, 201)
        self.assertFalse(Collection.objects.filter(collection_id=lotr_collection_id).exists())

        #Get collection count
        response_7 = self.client.post(f"collections/{pok_collection_id}/item-count/")
        self.assertEqual(response_7, 201)
        self.assertTrue(pokemon_coll.count(), 2)

        response_8 = self.client.post(f"collections/{lego_coll_id}/item-count/")
        self.assertEqual(response_7, 201)
        self.assertTrue(lego_coll, 2)
    def test_barcode_decode_valid(self):
        self.client.force_login(self.user)
        response = self.client.post("/api/scan-barcode/", {"image": "data:image/jpeg;base64,..."}, content_type="application/json")
        self.assertNotEqual(response.status_code, 500)

    def test_market_value_calculation(self):
        collection = Collection.objects.create(collection_type="video_games", name="Temp Collection", owner=self.user)
        item = Item.objects.create(collection=collection, name="Value Test", purchase_price=50.00, current_value=75.00)
        self.assertEqual(item.purchase_price, 50.00)
        self.assertEqual(item.current_value, 75.00)
        self.assertEqual(float(item.current_value - item.purchase_price), 25.00)

    def test_image_retrieval_fallback(self):
        collection = Collection.objects.create(collection_type="video_games", name="Temp Collection", owner=self.user)
        response = self.client.post("/api/items/add/", data=json.dumps({
            "collection_id": collection.id,
            "name": "No Image Item",
            "quantity": 1
        }), content_type="application/json")
        self.assertNotEqual(response.status_code, 500)
        item = Item.objects.filter(name="No Image Item").first()
        if item:
            self.assertTrue(item.image_url == "" or "placeholder" in item.image_url.lower())