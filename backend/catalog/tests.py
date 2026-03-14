from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Collection, Item

User = get_user_model()
class DeleteTests(TestCase):

    def setUp(self):
        self.client = Client()

        #create test owner
        self.user = User.objects.create(username="Test")

        #create test collection
        self.collection = Collection.objects.create(name="Delete Test Collection", owner=self.user)

        #create test item to be deleted
        self.item = Item.objects.create(name = "Item to delete", collection = self.collection)
        
    def test_delete_item_sucsess(self):
        
        #check if item exsists in collection before deletion
        self.assertTrue(Item.objects.filter(id=self.item.id).exists())

        #set url to delete the item
        url = f"/api/items/delete/{self.collection.id}/{self.item.id}/" 

        #try to delete the item and get its response
        response = self.client.delete(url)

        #check if status code is 200 (sucsess)
        self.assertEqual(response.status_code, 200)

        #check if item is not in the collection after deletion.
        self.assertFalse(Item.objects.filter(id=self.item.id).exists())

    def test_delete_item_not_exsist(self):

        #delete the only item in the collection (same as delete sucsess test)
        self.assertTrue(Item.objects.filter(id=self.item.id).exists())

        #save collection and item ids
        collectionId = self.collection.id
        itemId = self.item.id

        url = f"/api/items/delete/{collectionId}/{itemId}/" 
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)

        #check that item no longer exsists in the collection
        self.assertFalse(Item.objects.filter(id=self.item.id).exists())

        #try to delete the item again, which does not exsist
        url = f"/api/items/delete/{collectionId}/{itemId}/" 
        response = self.client.delete(url)

        #this should return error code 404, failed to delete item that does not exsist
        self.assertEqual(response.status_code, 404)        

