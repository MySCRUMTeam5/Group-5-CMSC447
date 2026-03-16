from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model
from .models import Collection, Item
from .views import sort_filter_collection
from datetime import date
import json

User = get_user_model()


class TestSortEmptyColl(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.collection = Collection.objects.create(name="Pokemon", owner=self.user)

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
        self.collection = Collection.objects.create(name="Pokemon", owner=self.user)

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
        self.collection = Collection.objects.create(name="Pokemon", owner=self.user)

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
        self.collection = Collection.objects.create(name="Pokemon", owner=self.user)

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