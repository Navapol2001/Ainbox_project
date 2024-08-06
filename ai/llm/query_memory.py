from pymongo import MongoClient
from datetime import datetime
import os
import dotenv
dotenv.load_dotenv()
class QueryMemory:
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
        """
        Constructs all the necessary attributes for the QueryMemory object.
        """
        self.client = MongoClient(os.environ.get('MONGO_DB_URI'))
        
        
    def query_memory(self,user_id : str,page_id : str) -> str:
        """
        Retrieves the chat history for a specific user and page.

        Parameters:
        user_id (str): The ID of the user.
        page_id (str): The ID of the page.

        Returns:
        str: The chat history.
        """
        
        filter={"log.data.user_id": user_id, "log.page_id": page_id}
        result = self.client['AI_Chat']['log_db'].find(filter=filter)
        history = []
        while result.alive:
            record = result.next()
            timestamp = datetime.fromtimestamp(record['log']['data']['timestamp'] / 1000.0)
            timestamp = timestamp.strftime('%Y-%m-%d %I:%M:%S %p')
            try :
                if record['log']['data']['user'] == duplicate_msg:
                    continue
            except:
                pass
            
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

   
   


# data = (QueryMemory().query_memory(user_id="Uef587cd99989e88348131011b60958be",page_id="Ub4ba514371a70b57f9ed28c8bdfcf9db"))
# print(data[-16:])