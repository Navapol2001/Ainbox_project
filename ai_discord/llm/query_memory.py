from datetime import datetime
from typing import Any

import dotenv
from llm.db import db_connect

dotenv.load_dotenv()


class QueryMemory(db_connect):
    """
    A class used to query and manage chat history from a MongoDB database.

    ...

    Attributes
    ----------
    client : pymongo.MongoClient
        a MongoDB client instance

    Methods
    -------
    query_memory(user_id, page_id):
        Retrieves the chat history for a specific user and page.
    memory(user_id, page_id):
        Retrieves the chat history for a specific user and page and returns it as a string.
    """

    def __init__(self):
        super().__init__()

    async def query_memory(self,
                     user_id: str,
                     page_id: str) -> list[dict[str, str | Any] | dict[str, str | Any]]:
        """
        Retrieves the chat history for a specific user and page.

        Parameters:
        user_id (str): The ID of the user.
        page_id (str): The ID of the page.

        Returns:
        str: The chat history.
        """

        duplicate_msg = None

        _filter = {"log.data.user_id": user_id,
                   "log.page_id": page_id}
        result = self.client['AI_Chat']['log_db'].find(filter=_filter)
        
        history = []
        while result.alive:
            record = result.next()
            timestamp = record['log']['data']['timestamp'].strftime('%Y-%m-%d %I:%M:%S %p')
            if record['log']['data']['user'] is duplicate_msg:
                continue

            user_chat = {
                'timestamp': timestamp,
                'user': record['log']['data']['user'],
                'chat': record['log']['data']['chat']
            }
            history.append(user_chat)
            duplicate_msg = record['log']['data']['user']

        # Mapping to conversational AI format
        conversation_history = []
        for record in history:
            conversation_history.append({"role": "user", "content": record['user']})

            conversation_history.append({"role": "assistant", "content": record['chat']})

        return conversation_history[-16:]
