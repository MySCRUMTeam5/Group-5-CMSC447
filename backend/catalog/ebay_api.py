import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("EBAY_CLIENT_SECRET_KEY")
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
            auth=(self.client_id, self.client_secret),
        )

        self.token = response.json().get("access_token")
        return self.token


    def fetch_items(self):
        if not self.token:
            self.get_ebay_token()
        
        url = f"{self.base_url}/buy/browse/v1/item_summary/search"

        headers = {
            "Authorization" : f"Bearer {self.token}",
            "Content-Type" : "application/json",
            "X-EBAY-C-MARKETPLACE-ID" : "EBAY_US",
        }

        response = requests.get(
            "https://api.sandbox.ebay.com/buy/browse/v1/item_summary/search",
            headers, params = {"q": query}
        )
    
    def parse_items(self):
        pass
    
    def post_items(self):
        pass
