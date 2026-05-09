import os
import requests
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("EBAY_CLIENT_SECRET")
API_ID = os.getenv("EBAY_CLIENT_ID")

class Ebay_API(object): #sets up class wrapper for ebay api calls
    def __init__(self):
        self.api_key = API_KEY
        self.api_id = API_ID
        self.base_url = "https://api.sandbox.ebay.com"
        self.token = None

    
    def get_ebay_token(self): #gets the token to access the ebay api
        url = f"{self.base_url}/identity/v1/oauth2/token"

        response = requests.post(
            url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "scope": "https://api.ebay.com/oauth/api_scope",
            },
            auth=(self.api_id, self.api_key),
        )

        self.token = response.json().get("access_token")
        return self.token


    def fetch_items(self, query): #calls to look up items
        if not self.token:
            self.get_ebay_token()
        
        url = f"{self.base_url}/buy/browse/v1/item_summary/search"

        headers = {
            "Authorization" : f"Bearer {self.token}",
            "Content-Type" : "application/json",
            "X-EBAY-C-MARKETPLACE-ID" : "EBAY_US",
        }

        response = requests.get(url, headers=headers, params={"q": query})

        return response.json()
        
    
    def parse_items(self, data):
        items = data.get("itemSummaries", [])

        return [ {
            "title" : item.get("title"),
            "price" : item.get("price", {}).get("value"),
            "condition" : item.get("condition")
            "image" : item.get("image", {}).get("imageUrl"),
            "url" : item.get("itemWebUrl")
        }
        for item in items
        ]