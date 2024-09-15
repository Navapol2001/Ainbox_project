import logging
from .db import db_connect
import httpx
import os
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.INFO)
LLM_ENDPOINT = os.getenv('LLM_ENDPOINT')

class MessageSender(db_connect):
    """
    A class used to send messages via discord.

    Attributes:
        client: A MongoDB client instance.
        generate_answer: An instance of the ChatAI class.
        discord_token: The discord account token.

    Methods:
        _chat_init: Initializes the ChatAI instance.
        get_account_token(page_id): Retrieves the account token for the specified page.
        send_message_discord(user_id, message, time_stamp, page_id): Sends a message to a user via discord.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the MessageSender object.
        """
        super().__init__()

        self._rank = {"EC1": r"/chat/ec/v1/",  
                    "IF1": r"/chat/info/v1/", 
                    }

    async def send_message_discord(self, 
                                   user_id: str, 
                                   message: str, 
                                   time_stamp: str, 
                                   page_id: str, 
                                   rank: str) -> tuple[dict[str, str], int] | tuple[dict[str, str], int]:
        """
        Sends a message to a user via discord.

        This method first initializes the ChatAI if it hasn't been initialized yet.
        It then retrieves the account token for the specified page.
        It logs the message and sends a response to the user.

        Args:
            user_id: The ID of the user to whom the message is sent.
            message: The message to be sent.
            time_stamp: The timestamp of the message.
            page_id: The ID of the page from which the message is sent.

        Raises:
            Exception: If the message fails to send.
        """
        #self._customer.create_customer(user_id=user_id, page_id=page_id)

        rank_func = self._rank.get(rank)
        
        # Prepare data for the POST request
        data = {
            "messages": message,
            "page_id": page_id,
            "user_id": user_id
        }

       # Send the POST request
        async with httpx.AsyncClient() as client:
            response = await client.post(url=f"http://{LLM_ENDPOINT}:8000{rank_func}", json=data)

        # Process the response
        if response.status_code == 200:
            answer = response.json()
        else:
            # Handle non-200 status codes appropriately
            return {"error": "Request failed"}, response.status_code
        
        method = "discord"
        await self.log_message(method=method, 
                         page_id=page_id, 
                         user_id=user_id, 
                         message=message, 
                         answer=answer, 
                         time_stamp=time_stamp)
        return answer

    async def send_message_not_text(self, 
                              method: str, 
                              user_id: str, 
                              page_id: str, 
                              time_stamp: str, 
                              message="Message not text") -> None:
        """
        Sends a non-text message to a user.

        This method first initializes the chat AI if it hasn't been initialized yet.
        It then retrieves the account token for the specified page.
        It logs the message and sends a response to the user indicating that the input was not valid.

        Args:
            method: The method used to send the message.
            user_id: The ID of the user to whom the message is sent.
            page_id: The ID of the page from which the message is sent.
            time_stamp: The timestamp of the message.
            message: The message to be sent. Defaults to "message not text".

        Raises:
            Exception: If the message fails to send.
        """
        if self._chat_state is None:
            self._chat_init()

        await self.log_message(method=method, page_id=page_id, user_id=user_id, message=message, answer=None, time_stamp=time_stamp)
        return None

    async def bot_inactive_react(self, 
                           method: str, 
                           user_id: str, 
                           page_id: str, 
                           time_stamp: str, 
                           message: str):
        """
        Sends a message to a user when the bot is inactive.
        """
        await self.log_message(method=method, 
                         page_id=page_id, 
                         user_id=user_id, 
                         message=message, 
                         answer=None, 
                         time_stamp=time_stamp)
        return None

    async def log_message(self, 
                          page_id: str, 
                          method: str, 
                          user_id: str, 
                          message: str, 
                          answer: str, 
                          time_stamp: str) -> None:
        """
        Logs a message.

        Args:
            page_id: The ID of the page.
            method: The method used.
            user_id: The ID of the user.
            message: The message.
            answer: The answer.
            time_stamp: The timestamp.
        """
        if type(answer) is not dict:
            log_data = {
                "method": method,
                "log": {
                    "page_id": page_id,
                    "data": {
                        'timestamp': time_stamp,
                        'user_id': user_id,
                        'user': message,
                        'chat': answer,
                        'customer_feeling': None,
                        'topic': None
                    }
                }
            }
        else:
            log_data = {
                "method": method,
                "log": {
                    "page_id": page_id,
                    "data": {
                        'timestamp': time_stamp,
                        'user_id': user_id,
                        'user': message,
                        'chat': answer['answer'],
                        'customer_feeling': answer['customer_feeling'],
                        'topic': answer['topic']
                    }
                }
            }
        mydb = self.client["AI_Chat"]
        mycol = mydb["log_db"]
        mycol.insert_one(log_data)