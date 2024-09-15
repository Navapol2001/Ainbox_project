from pymongo import MongoClient
import os


class db_connect:
    def __init__(self):
        self.client = MongoClient(os.environ.get('MONGO_DB_URI'))

    def get_db_data(self, page_id: str) -> dict:
        """Get store data from database"""
        _filter = {'page_id': page_id}
        store_db = self.client['AI_Chat']['store_db'].find_one(_filter)
        if store_db:
            return store_db['details']
        else:
            raise ValueError("No data found for the given page_id")
