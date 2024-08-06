from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import logging
load_dotenv()
class Consumption():
    def __init__(self):
        self.client = MongoClient(os.environ.get('MONGO_DB_URI'))

    def consumption_log_msg(self,page_id:str,prompt_input:int,prompt_output:int ,cost:float,model:str) -> None  :
        memory =self.client['AI_Chat']
        token = memory['consumption_log']
        used = {"page_id": page_id, "time": datetime.now(),"model": model ,"prompt_input": int(prompt_input),"prompt_output": int(prompt_output),"total_prompt":int(prompt_input) + int(prompt_output), "cost": round(cost,6)}
        token.insert_one(used)


    


