import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from typing import Union
logging.basicConfig(level=logging.INFO)

class QuotaCheck:
    """
    A class for checking and decreasing quotas for a bot.

    Attributes:
        client (MongoClient): The MongoDB client.
        db (Database): The MongoDB database.
        collection (Collection): The MongoDB collection for bot quotas.

    Methods:
        check_quota: Retrieves the quota for a given page ID.
        decrease_quota: Decreases the quota for a given page ID.
    """

    def __init__(self) -> None:
        try:
            self.client = MongoClient(os.getenv('MONGO_DB_URI'))
            self.db = self.client['AI_Chat']
        except ConnectionFailure:
            logging.info("MongoDB connection failed. Check your MONGO_DB_URI.")
            return None


    async def check_status(self,page_id) -> bool:
        """Check Status of bot"""
        status_collection = self.db['status_check']
        
        status = status_collection.find_one({'page_id': page_id})
        print(status)
        if not status:
            logging.info(f"page_id:{page_id} not found")
            return None
        if status['status'] == 1:
            return True
        else:
            return False
            
    async def check_quota(self, page_id: str) -> Union[bool, None]:
        """
        Checks the quota for a given page ID in the new bot_quota structure.

        Args:
            page_id (str): The ID of the page.

        Returns:
            bool: True if quota is available, False if quota is depleted.
            None: If no quota record is found for the page.
        """
        collection = self.db['bot_quota']
        
        # Find the document that contains the given page_id
        quota_doc = collection.find_one(
            {"page_id": page_id}
        )

        if not quota_doc:
            logging.info(f"No quota record found for page_id: {page_id}")
            return None

        # Check if quota is available
        if quota_doc['quota'] > 0:
            return True
        else:
            return False

    async def decrease_quota(self, page_id: str) -> bool:
        """
        Decreases the quota for a given page ID in the new bot_quota structure.

        Args:
            page_id (str): The ID of the page.

        Returns:
            bool: True if the quota was successfully decreased, False otherwise.
        """
        collection = self.db['bot_quota']
        
        # Find and update the document that contains the given page_id
        result = collection.update_one(
            {"page_id": page_id},  # Corrected filter
            {"$inc": {"quota": -1}}
        )

        if result.modified_count > 0:
            logging.info(f"Quota decreased for page_id: {page_id}")
            return True
        else:
            logging.info(f"Failed to decrease quota for page_id: {page_id}")
            return False

    
class tier(QuotaCheck):
    def __init__(self) -> None:
        super().__init__()
    async def get_tier(self,page_id):
        filter={
            'page_id': page_id
        }
        tier = self.db['tier_status'].find(
        filter=filter)
        try :
            
            return tier[0]['tier']
        except:
            return None

    

# class customer_status(QuotaCheck):
#     def __init__(self) -> None:
#         super().__init__()
#     async def get_status(self, page_id , user_id):
#         filter={
#             'page_id': page_id , 'line_user_id':user_id
#         }
#         status =  self.db['customer_status'].find_one(filter)
        
#         # Check if data exists and if the status is 1
#         if status and status.get('status') == 1:
#             return True
#         elif status and status.get('status') == 0:
#             return False
#         else:
#             return True