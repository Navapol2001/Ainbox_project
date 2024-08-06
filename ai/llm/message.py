import requests
from .llm import ChatAI 
import pymongo
import os
import logging
logging.basicConfig(level=logging.INFO)
from .agent.prompt.prompt_system import db_connect

class message_sender(db_connect):
    """
    A class used to send messages via LINE.

    ...

    Attributes
    ----------
    client : pymongo.MongoClient
        a MongoDB client instance
    generate_answer : ChatAI
        an instance of the ChatAI class
    Line_token : str
        the LINE account token

    Methods
    -------
    initialize_chat_ai():
        Initializes the ChatAI instance.
    get_account_token(page_id):
        Retrieves the account token for the specified page.
    send_message_line(user_id, message, time_stamp, page_id):
        Sends a message to a user via LINE.
    """    
    def __init__(self):
        """
        Constructs all the necessary attributes for the message_sender object.
        """
        super().__init__()
        self.customer = Create_customer()
        self.status = Human_Handle()
        self.generate_answer = None
        self.anwser_unrecognized = "ตอนนี้ระบบยังไม่รองรับข้อความอื่นนอกจากข้อความน้าา 🙏"
        self.rank = {"EC1": "_chat_e_v1", "EC2": "_chat_e_v2", "IF1": "_chat_info_v1", "IF2": "_chat_info_v2"}

    def initialize_chat_ai(self):
        """
        Initializes the ChatAI instance.
        """
        self.generate_answer = ChatAI()
    
    def get_account_token(self,page_id):
        """
        Retrieves the account token for the specified page.

        Parameters:
        page_id (str): The ID of the page.

        Returns:
        str: The account token.
        """
        
        filter = {"page_id": page_id}
        result = self.client['AI_Chat']['page_account'].find(filter=filter)
        Line_token = result[0]['page_access_token']
        return Line_token
        
    def send_message_line(self, user_id:str, message:str, time_stamp:str ,page_id:str , rank:str) -> None:
        """
        Sends a message to a user via LINE.

        This method first initializes the ChatAI if it hasn't been initialized yet.
        It then retrieves the account token for the specified page.
        It logs the message and sends a response to the user.

        Parameters:
        user_id (str): The ID of the user to whom the message is sent.
        message (str): The message to be sent.
        time_stamp (str): The timestamp of the message.
        page_id (str): The ID of the page from which the message is sent.

        Raises:
        Exception: If the message fails to send.
        """
        self.customer.create_customer(user_id=user_id, page_id=page_id)
        if self.generate_answer is None:
            self.initialize_chat_ai()
        Line_token = self.get_account_token(page_id)
        chat  = self.rank[rank]
        answer = getattr(self.generate_answer, chat)(messages=message, page_id=page_id, user_id=user_id)
        method = "line"
        self.log_message(method=method,
                         page_id=page_id,
                         user_id=user_id, 
                         message=message, 
                         answer=answer, 
                         time_stamp=time_stamp)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {Line_token}'
        }
        data = {
            "to": f"{user_id}",
            "messages": [
                {
                    "type": "text",
                    "text": f"{answer['answer']}"
                }
            ]
        }
        try:
            response = requests.post('https://api.line.me/v2/bot/message/push', headers=headers, json=data)
            if response.status_code == 200:
                logging.info('Message sent successfully.')
                if int(answer['answer_able']) == 0:
                    self.sent_line_notify(page_id=page_id, user_id=user_id, message=message, answer=answer)
                    self.status.set_status(page_id=page_id, user_id=user_id)
                return {"status": "ok"}, 200
            else:
                return {"status": "error", "error_message": "Failed to send message to LINE."}, 500
        except Exception as e:
            raise e

    def send_message_not_text(self,method, user_id,page_id ,time_stamp, message="Message not text"):
       
        """
        Sends a non-text message to a user.

        This method first initializes the chat AI if it hasn't been initialized yet.
        It then retrieves the account token for the specified page.
        It logs the message and sends a response to the user indicating that the input was not valid.

        Parameters:
        method (str): The method used to send the message.
        user_id (str): The ID of the user to whom the message is sent.
        page_id (str): The ID of the page from which the message is sent.
        time_stamp (str): The timestamp of the message.
        message (str, optional): The message to be sent. Defaults to "message not text".

        Raises:
        Exception: If the message fails to send.
        """        
        
        if self.generate_answer is None:
            self.initialize_chat_ai()
        Line_token = self.get_account_token(page_id)
        self.log_message(method=method,
                         page_id=page_id,
                         user_id=user_id, 
                         message=message, 
                         answer=self.anwser_unrecognized, 
                         time_stamp=time_stamp)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {Line_token}'
        }
        data = {
            "to": f"{user_id}",
            "messages": [
                {
                    "type": "text",
                    "text": self.anwser_unrecognized
                }
            ]
        }
        response = requests.post('https://api.line.me/v2/bot/message/push', headers=headers, json=data)
        if response.status_code == 200:
            logging.info('Message sent successfully.')
            self.sent_line_notify(page_id=page_id, user_id=user_id, message=message, answer=self.anwser_unrecognized)
        else:
            raise Exception('Failed to send message to LINE.')
    def bot_inactive_react(self,method, user_id,page_id ,time_stamp, message):
        
        """
        Sends a message to a user when the bot is inactive.
        """
 
        if self.generate_answer is None:
            self.initialize_chat_ai()
        Line_token = self.get_account_token(page_id)
        self.log_message(method=method,
                         page_id=page_id,
                         user_id=user_id, 
                         message=message, 
                         answer="เดี๋ยวเจ้าหน้าที่จะตอบกลับภายในไม่ช้าน้าาา", 
                         time_stamp=time_stamp)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {Line_token}'
        }
        data = {
            "to": f"{user_id}",
            "messages": [
                {
                    "type": "text",
                    "text": "เดี๋ยวเจ้าหน้าที่จะตอบกลับภายในไม่ช้าน้าาา 😊"
                }
            ]
        }
        response = requests.post('https://api.line.me/v2/bot/message/push', headers=headers, json=data)
        if response.status_code == 200:
            logging.info('Message sent successfully.')
        else:
            raise Exception('Failed to send message to LINE.')
        
    def log_message(self,page_id,method, user_id, message, answer, time_stamp):
        
        """
        Logs a message with a specified level.

        Parameters:
        message (str): The message to be logged.
        level (str, optional): The level of the log. Defaults to 'INFO'.

        Returns:
        None
        """
        
        if type(answer) != dict:
            log_data = {
                "method":method,
                "log":
                    {
                    "page_id":page_id,
                    "data": {
                        'timestamp': time_stamp,
                        'user_id': user_id,
                        'user': message,
                        'chat': answer,
                        'customer_feeling': None,
                        'topic':None
                    }
                }
            }
        else:
            log_data = {
                "method":method,
                "log":
                    {
                    "page_id":page_id,
                    "data": {
                        'timestamp': time_stamp,
                        'user_id': user_id,
                        'user': message,
                        'chat': answer['answer'],
                        'customer_feeling': answer['customer_feeling'],
                        'topic':answer['topic']
                    }
                }
            }
        mydb = self.client["AI_Chat"]
        mycol = mydb["log_db"]
        mycol.insert_one(log_data)
    
    def sent_line_notify(self,page_id, user_id, message, answer):
        """
        Send message to line notify
        """
        token = self.get_token_notify(page_id)
        if type(answer) != dict:
            message = f"""\nTopic : None \n🙋‍♂️ User : {message} \n🤖AI : {answer} \n🙂 : None \nUser ID : {user_id} """
        else:
            message = f"""\nTopic : {answer['topic']} \n🙋‍♂️ User : {message} \n🤖AI : {answer['answer']} \n🙂 : {answer['customer_feeling']} \nUser ID : {user_id} """
                    
        url = "https://notify-api.line.me/api/notify"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {token}'}
        r = requests.post(url, headers=headers, data = {'message':message})
        if r.status_code == 200:
            logging.info('Line notify sent successfully.')

    def get_token_notify(self,page_id):
        """
        Retrieves the account token for the specified page.

        Parameters:
        page_id (str): The ID of the page.

        Returns:
        str: The account token.
        """
        filter = {"page_id": page_id}
        result = self.client['AI_Chat']['page_account'].find(filter=filter)
        notfy_token = result[0]['line_notify']
        return notfy_token
    
    
class Human_Handle(db_connect):
    def __init__(self) -> None:
        super().__init__()
    def set_status(self,page_id,user_id):
        status = 0
        filter = {'page_id': page_id , 'user_id': user_id}
        self.client['AI_Chat']['customer_status'].find_one_and_update(filter=filter, update={'$set': {'status': status}})

class Create_customer(db_connect):
    def __init__(self) -> None:
        super().__init__()
    def create_customer(self, page_id, user_id):
        # Check if the user_id already exists in the collection
        existing_user = self.client['AI_Chat']['customer_status'].find_one({'user_id': user_id})
        
        if existing_user:
            pass
        else:
            data = {'page_id': page_id, 'user_id': user_id, 'status': 1}
            # Insert the data with upsert=True to ensure uniqueness
            self.client['AI_Chat']['customer_status'].update_one(
                {'user_id': user_id},
                {'$set': data},
                upsert=True
            )

