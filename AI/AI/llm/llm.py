import json
import os
import logging
from litellm import completion, completion_cost
from litellm.caching import Cache
import litellm
import enum
from typing import List, Optional, Any
from .query_memory import QueryMemory
from .consumption import Consumption
from .agent.prompt.ecommerce import Ecommerce 
from .agent.prompt.info import Information 
import dotenv
from pydantic import BaseModel
logging.basicConfig(level=logging.INFO)

dotenv.load_dotenv()
litellm.success_callback = ["langfuse"]
litellm.failure_callback = ["langfuse"]  # logs errors to langfuse
# Make completion calls
os.environ["LANGFUSE_PUBLIC_KEY"] = os.getenv('LANGFUSE_PUBLIC_KEY')
os.environ["LANGFUSE_SECRET_KEY"] = os.getenv('LANGFUSE_SECRET_KEY')

class Topics(enum.Enum):
    CONSULT = "consult"
    ORDER = "order"
    COMPLAINT = "complaint"
    GENERAL = "general"
    PRODUCT = "product"
    OTHER = "other"

class Feeling(enum.Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    NEUTRAL = "neutral"

class Actions(enum.Enum):
    Actions = "direct_response"


class Answerable(enum.Enum):
    YES = 1
    NO = 0

class Ecomerce_Response(BaseModel):
  answer_response: str
  topic: Topics
  action: Actions
  customer_feeling: Feeling
  answer_able:Answerable

class Information_Response(BaseModel):
  answer_response: str
  topic: Topics
  action: Actions
  customer_feeling: Feeling
    


MODEL = os.getenv('MODEL')
MODEL_API = os.getenv('MODEL_API_KEY')


def clean_msg(msg: str | dict[str, str | Any]) -> dict[Any, Any] | str:
    # import re
    """
    ทำความสะอาดข้อความโดยการลบอักขระและการจัดรูปแบบที่เฉพาะเจาะจง

    Args:
    - msg (str): ข้อความที่จะทำความสะอาด

    Returns:
    - str: ข้อความที่ทำความสะอาดแล้ว
    """
    cleaned_msg = {
        key: value.replace("**", "").replace("##", "#").replace("*", "•").replace("\n\n", "\n").replace("  ",
                                                                                                        " ").strip()
        for key, value in msg.items()}

    return cleaned_msg


def clean_json_tag(text: str) -> str:
    """
    ทำความสะอาดแท็ก JSON จากข้อความ

    Args:
    - text (str): ข้อความที่มีแท็ก JSON

    Returns:
    - str: ข้อความที่ไม่มีแท็ก JSON
    """
    return text.replace('```json', '').replace('```', '')


class ChatAI:
    """
    A class used to represent a Chat AI.

    Attributes:
    - memory (QueryMemory): An instance of the QueryMemory class for querying memory.
    - cal_con (Consumption): An instance of the Consumption class for handling consumption logs.
    - dict_chat (dict): A dictionary to store chat history.

    Methods:
    - chat_activate(page_id: str, rank: int, history: Optional[List[dict]] = None) -> None:
        Activates the chat with the specified page and rank, optionally using provided history.
    - chat_v1(messages: str, page_id: str, user_id: str) -> str:
        Handles the chat flow, stores the chat history, and returns the response.
    - prompt_activate(page_id: str, rank: int) -> str:
        Returns a prompt template based on the page ID and rank.
    - clean_msg(msg: str) -> str:
        Cleans the message by removing specific characters and formatting.
    - clean_json_tag(text: str) -> str:
        Cleans the JSON tags from the text.
    """

    def __init__(self):
        """
        Initializes the ChatAI instance.
        """
        self.e_prompt = Ecommerce()
        self.i_prompt = Information()
        self.memory = QueryMemory()
        self.cal_con = Consumption()
        self.dict_chat = {}

    def chat_activate(self,
                      page_id: str,
                      rank: str,
                      history : Optional[List[dict]] = None
                    ) :
        """
        เปิดใช้งานการสนทนาด้วยหน้าและอันดับที่ระบุ โดยเลือกใช้ประวัติการสนทนาที่ให้มา (ถ้ามี)

        Args:
        - page_id (str): ID ของหน้าที่เปิดใช้งานการสนทนา
        - rank (str): อันดับของการสนทนา
        - history (List[dict], optional): ประวัติการสนทนา ค่าเริ่มต้นคือ None
        """

        system_instruction = self.prompt_activate(page_id, rank)
        if history:
            messages = [{"content": system_instruction, "role": "system"}, *history]
            logging.info('Memory are Called')
            return messages
        else:
            messages = [{"content": system_instruction, "role": "system"}]
            logging.info(messages)
        
            logging.info('No Memory are Called')

            return messages

    async def CHAT_EC_V1(self,
                   messages: str,
                   page_id: str,
                   user_id: str) -> dict[Any, Any]:

        """
        จัดการการไหลของการสนทนา บันทึกประวัติการสนทนา และส่งคืนคำตอบ

        Args:
        - messages (str): ข้อความที่จะส่ง
        - page_id (str): ID ของหน้าที่ส่งข้อความ
        - user_id (str): ID ของผู้ใช้ที่ส่งข้อความ

        Returns:
        - str: คำตอบจากแบบจำลองการสนทนา
        """

        rank = "EC1"
        if page_id not in self.dict_chat:
            try:
                memory =  await self.memory.query_memory(user_id=user_id, page_id=page_id)
                chat_session = self.chat_activate(page_id=page_id, history=memory, rank=rank)
            except Exception as e:
                logging.error(f"New user {user_id} on page {page_id} \n {e}")
                chat_session = self.chat_activate(page_id=page_id, rank=rank)

            self.dict_chat[page_id] = chat_session
        else:
            chat_session = self.dict_chat[page_id]

        self.dict_chat[page_id].append({"role": "user", "content": messages})

        ######################################### Model Answer ##########################################
        while True:
            response = completion(
                model=MODEL,  # เปลี่ยน Model Name และ API เพื่อเปลี่ยนค่าย AI
                messages=chat_session.copy(),
                api_key=MODEL_API,
                user=page_id,
                response_format=Ecomerce_Response
            )
            # logging.info(chat_session)
            ##################################################################################################
            dict_answer = response.choices[0].message.content
            cost = completion_cost(model=self.model, messages=chat_session)
            self.dict_chat[page_id].append({"role": "assistant", "content": dict_answer})
            self.cal_con.consumption_log_msg(page_id=page_id, model=response['model'],
                                             prompt_input=response['usage']['prompt_tokens'],
                                             prompt_output=response['usage']['completion_tokens'], cost=cost)
            try:
                dict_answer = json.loads(clean_json_tag(dict_answer))
                break  # Exit the loop if JSON parsing is successful
            except json.JSONDecodeError:
                self.dict_chat[page_id].append({"role": "user",
                                                "content": f"# WARNING \n You Answer in Wrong Format \n "
                                                           f"Make Answer Following System Instruction"})
                # Continue the loop if there's an error
        ############################### Change Chat Tier Functions Here ##################################
        # logging.info(dict_answer)
        llm_answer = {"answer": dict_answer['answer_response'], "customer_feeling": dict_answer['customer_feeling'],
                      "topic": dict_answer['topic'], "answer_able": str(dict_answer['answer_able'])}
        return clean_msg(llm_answer)
    async def CHAT_EC_V2(self):
        pass
    async def CHAT_INFO_V1(self,
                   messages: str,
                   page_id: str,
                   user_id: str) -> dict[Any, Any]:
        
        """
        จัดการการไหลของการสนทนา บันทึกประวัติการสนทนา และส่งคืนคำตอบ

        Args:
        - messages (str): ข้อความที่จะส่ง
        - page_id (str): ID ของหน้าที่ส่งข้อความ
        - user_id (str): ID ของผู้ใช้ที่ส่งข้อความ

        Returns:
        - str: คำตอบจากแบบจำลองการสนทนา
        """

        rank = "IF1"
        if page_id not in self.dict_chat:
            try:
                memory =  await self.memory.query_memory(user_id=user_id, page_id=page_id)
                chat_session = self.chat_activate(page_id=page_id, history=memory, rank=rank)
            except Exception as e:
                logging.error(f"New user {user_id} on page {page_id} \n {e}")
                chat_session = self.chat_activate(page_id=page_id, rank=rank)

            self.dict_chat[page_id] = chat_session
        else:
            chat_session = self.dict_chat[page_id]

        self.dict_chat[page_id].append({"role": "user", "content": messages})

        ######################################### Model Answer ##########################################
        while True:
            response = completion(
                model=MODEL,  # เปลี่ยน Model Name และ API เพื่อเปลี่ยนค่าย AI
                messages=chat_session.copy(),
                api_key=MODEL_API,
                user=page_id,
                response_format=Information_Response
                
            )
            # logging.info(chat_session)
            ##################################################################################################
            dict_answer = response.choices[0].message.content
            cost = completion_cost(model=MODEL, messages=chat_session)
            self.dict_chat[page_id].append({"role": "assistant", "content": dict_answer})
            self.cal_con.consumption_log_msg(page_id=page_id, model=response['model'],
                                             prompt_input=response['usage']['prompt_tokens'],
                                             prompt_output=response['usage']['completion_tokens'], cost=cost)
            try:
                dict_answer = json.loads(clean_json_tag(dict_answer))
                break  # Exit the loop if JSON parsing is successful
            except json.JSONDecodeError:
                self.dict_chat[page_id].append({"role": "user",
                                                "content": "# WARNING \n You Answer in Wrong Format \n "
                                                           "Make Answer Following System Instruction \n"
                                                           """Answer Following this format:{"answer_response": "string", 
                                                           "topic": "string", 
                                                           "action": "direct_response", 
                                                           "customer_feeling": "string" } """})
                # Continue the loop if there's an error
        ############################### Change Chat Tier Functions Here ##################################
        # logging.info(dict_answer)
        llm_answer = {"answer": dict_answer['answer_response'], "customer_feeling": dict_answer['customer_feeling'],
                      "topic": dict_answer['topic']}
        return clean_msg(llm_answer)
    
    async def CHAT_INFO_V2(self):
        pass


    def prompt_activate(self,
                        page_id: str,
                        rank: str) -> str:
        """
        ส่งคืนเทมเพลตพรอมต์ตาม ID ของหน้าและอันดับ

        Args:
        - page_id (str): ID ของหน้าที่เปิดใช้งานพรอมต์
        - rank (int): อันดับของพรอมต์

        Returns:
        - str: เทมเพลตพรอมต์
        """
        
        if str(rank) in ["EC1", "EC2"]:
            return self.e_prompt.generate_admin_prompt(page_id, rank)
        elif str(rank) in ["IF1", "IF2"]:
            logging.info(f"Rank: {rank}")
            logging.info(f"Page ID: {page_id}")
            return self.i_prompt.generate_admin_prompt(page_id, rank)
