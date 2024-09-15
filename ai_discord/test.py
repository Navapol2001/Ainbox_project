# !gcloud auth application-default login - run this to add vertex credentials to your env
import litellm, os
import enum
import dotenv
dotenv.load_dotenv()
import json
from litellm import completion 
from pydantic import BaseModel 

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

    
messages=[
        {"role": "system", "content": "Answer user with answer_response and analyze user feeling"},
        {"role": "user", "content": "สวัสดีคับเป็นยังไงบ้างครับ"},
    ]

litellm.enable_json_schema_validation = True
os.environ['LITELLM_LOG'] = 'DEBUG'


resp = completion(
    model="gemini/gemini-1.5-flash",
    messages=messages,
    response_format=Ecomerce_Response,
    api_key=os.getenv('MODEL_API_KEY')
)
data = json.loads(resp.choices[0].message.content)
print(data)
print(type(data))
