from datetime import datetime
from dotenv import load_dotenv
from llm.db import db_connect

load_dotenv()


class Consumption(db_connect):
    def __init__(self):
        super().__init__()

    def consumption_log_msg(self, 
                            page_id: str, 
                            prompt_input: int, 
                            prompt_output: int, 
                            cost: float, 
                            model: str) -> None:
        
        memory = self.client['AI_Chat']
        token = memory['consumption_log']
        used = {"page_id": page_id, 
                "time": datetime.now(), 
                "model": model, 
                "prompt_input": int(prompt_input),
                "prompt_output": int(prompt_output), 
                "total_prompt": int(prompt_input) + int(prompt_output),
                "cost": round(cost, 6)}
        token.insert_one(used)
