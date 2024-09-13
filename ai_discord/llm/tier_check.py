from pymongo import MongoClient
import os 
import dotenv
dotenv.load_dotenv()

class Tier_Check:
    """
    A class that checks the tier status for a given page_id.

    Attributes:
        client (MongoClient): The MongoDB client.
        db (MongoDatabase): The MongoDB database.
        collection (MongoCollection): The MongoDB collection.

    Methods:
        check_tier: Retrieves the tier status for a given page_id.

    """

    def __init__(self):
        self.client = MongoClient(os.getenv('MONGO_DB_URI'))
        self.db = self.client['AI_Chat']
        self.collection = self.db['tier_status']

    def check_tier(self, page_id):
        """
        Retrieves the tier status for a given page_id.

        Args:
            page_id (str): The ID of the page.

        Returns:
            str or None: The tier status of the page, or None if not found.

        """
        tier = self.collection.find_one({'page_id': page_id})
        if not tier:
            return None
        return tier['tier']
        
