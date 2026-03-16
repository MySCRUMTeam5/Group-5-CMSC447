import json
from django.test import TestCase, Client
from .models import User, Collection, Item


class AddItemTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.collection = Collection.objects.create(owner=self.user, name="Pokemon Cards")

    def test_cant_add_empty_item(self):
        response = self.client.post("/api/items/add/",
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_cant_add_without_collection_id(self):
        response = self.client.post("/api/items/add/",
            data=json.dumps({
                "name": "Charizard"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_cant_add_without_name(self):
        response = self.client.post("/api/items/add/",
            data=json.dumps({
                "collection_id": self.collection.id
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_cant_add_without_collection_id_and_name(self):
        response = self.client.post("/api/items/add/",
            data=json.dumps({
                "category": "cards"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)