from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from .models import Collection, Item
from .views import sort_filter_collection
from datetime import date
import json

#Things to Test:
    #Sorting an empty list newest to oldest and oldest to newest
    #Sorting an empty collection newest to oldest and oldest to newest
    #Sorting the list by most $$ to least $$ (normal case)
    #Sorting the list by least $$ to most $$ (normal case)
    #Sorting an empty list least $$ to most $$ and most $$ to least $$
    #Sorting an empty collection least $$ to most $$ and most $$ to least $$


class TestNoColl(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_sort_a_z_no_coll(self):
        #Sorting a collection that doesn't exist
        request = self.factory.get("/items/?sort=alpha_ascend")

        response = sort_filter_collection(request)

        self.assertEqual(response.status_code, 200)
    
    def test_sort_z_a_no_coll(self):
        #Sorting a collection that doesn't exist
        request = self.factory.get("/items/?sort=alpha_descend")

        response = sort_filter_collection(request)

        self.assertEqual(response.status_code, 200)

class TestSortEmptyColl(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        Pokemon = Collection.objects.create(name="Pokemon")

    def test_sort_a_z_empty(self):
        #Sorting an empty list A-Z
        request = self.factory.get("/items/?sort=alpha_ascend")

        response = sort_filter_collection(request)

        data = json.loads(response.content)

        expected_order = []

        actual_order = [item["name"] for item in data]

        self.assertEqual(actual_order, expected_order)

    def test_sort_z_a_empty(self):
        #Sorting an empty list Z-A
        request = self.factory.get("/items/?sort=alpha_descend")

        response = sort_filter_collection(request)

        data = json.loads(response.content)

        expected_order = []

        actual_order = [item["name"] for item in data]

        self.assertEqual(actual_order, expected_order)


## ------------------------------------ PASSED TESTS ------------------------------------##
class TestSortAlphaNormal(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
        User = get_user_model()
        
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        
        self.collection = Collection.objects.create(name="Pokemon", owner=self.user)
        
        Item.objects.create(collection=self.collection, name="Fire Red")
        Item.objects.create(collection=self.collection, name="Silver")
        Item.objects.create(collection=self.collection, name="Crystal")
        Item.objects.create(collection=self.collection, name="Gold")
        Item.objects.create(collection=self.collection, name="Leaf Green")

    def test_sort_a_z_normal(self):
        #Sorting a list A-Z alphabetically (normal case)
        request = self.factory.get("/items/?sort=alpha_ascend")

        response = sort_filter_collection(request)
        
        data = json.loads(response.content)
           
        expected_order = ["Crystal", "Fire Red", "Gold", "Leaf Green", "Silver"]

        actual_order = [item["name"] for item in data]

        self.assertEqual(actual_order, expected_order)

    def test_sort_z_a_normal(self):
        #Sorting a list Z-A alphabetically (normal case)
        request = self.factory.get("/items/?sort=alpha_descend")

        response = sort_filter_collection(request)
        
        data = json.loads(response.content)
          
        expected_order = ["Silver", "Leaf Green", "Gold", "Fire Red", "Crystal"]

        actual_order = [item["name"] for item in data]

        self.assertEqual(actual_order, expected_order)

class TestSortDateNormal(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        User = get_user_model()
        
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        
        self.collection = Collection.objects.create(name="Pokemon", owner=self.user)
        
        Item.objects.create(collection=self.collection, name="Fire Red", purchase_date=date(2025, 8, 10))
        Item.objects.create(collection=self.collection, name="Silver", purchase_date=date(2025, 7, 10))
        Item.objects.create(collection=self.collection, name="Crystal", purchase_date=date(2026, 3, 10))
        Item.objects.create(collection=self.collection, name="Gold", purchase_date=date(2024, 8, 10))
        Item.objects.create(collection=self.collection, name="Leaf Green", purchase_date=date(2026, 3, 16))
    
    def test_sort_date_ascend_normal(self):
        #Sorting a list oldest to newest (normal case)
        request = self.factory.get("/items/?sort=date_ascend")

        response = sort_filter_collection(request)

        data = json.loads(response.content)
           
        expected_order = ["Gold", "Silver", "Fire Red", "Crystal", "Leaf Green"]

        actual_order = [item["name"] for item in data]

        self.assertEqual(actual_order, expected_order)

    def test_sort_date_descend_normal(self):
        #Sorting a list newest to oldest (normal case)
        request = self.factory.get("/items/?sort=date_descend")

        response = sort_filter_collection(request)

        data = json.loads(response.content)
           
        expected_order = ["Leaf Green", "Crystal", "Fire Red", "Silver", "Gold"]

        actual_order = [item["name"] for item in data]

        self.assertEqual(actual_order, expected_order)