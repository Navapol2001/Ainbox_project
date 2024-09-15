import re
import logging
from llm.db import db_connect

# import dotenv
# dotenv.load_dotenv()


def _example_() -> str:
    return """
USER : ขอคุยกับแอดมินเพจ,ขอคุยกับคน,
MODEL :```json
    {
    "answer_response": "ได้เลยครับ รอสักครู่ ผมจะโอนสายไปหาแอดมินให้ครับ 😊",
    "topic": "general",
    "action": "direct_response",
    "customer_feeling": "happy",
    "answer_able": 0
    }```,
    
"""


def _add_rank1_rules() -> str:
    return """- **Always follow** our product and business information precisely.\n

\n- You cannot receive an order from the user and process it.
\nWhen responding, MUST output a response in this format:

\n```json\n
    {\n
    "answer_response": string, \\ You should put what you want to return to use here
    "topic": string, \\ The topic of the conversation. Must be one of consult, order , complaint , general , product , \
    other
    "action": "direct_response", \\ Must be "direct_response
    "customer_feeling": string, \\ The feeling of the customer must be one of (happy, sad, angry, neutral)
    "answer_able : int \\ 1 = Able to answer within given context ,0 = if cannot answer within context , call for human 
    \n}
    \n```"""


def _add_rank2_rules() -> str:
    return """When responding, MUST output a response in this format:
\n```json\n
    {\n
    "answer_response": string, \\ You should put what you want to return to use here
    "topic": string, \\ The topic of the conversation. Must be one of consult, order , complaint , general , product , \
    other
    "action": "direct_response", \\ Must be "direct_response
    "customer_feeling": string, \\ The feeling of the customer must be one of (happy, sad, angry, neutral)
    \n}
    \n```"""



def _add_rules(rank: str) -> str:
    rules = """\nStrict Rules:\n
    - If user asks you a question unrelated to our business, **politely decline.**\n
    - **Stay Within Your Boundaries:**  If a customer asks a question outside of scope, politely inform them that \
    you can't answer that.
    - Keep responses **short **\n
    - **Stick to the facts** about our products and services. Don't make anything up.\n
    - **Concise answers** are best. \n
    - **No unnecessary emojis.**\n
    - For questions that require human assistance\n
    """
    if rank is "EC1":
        rules += _add_rank1_rules()
    else:
        rules += _add_rank2_rules()
    return rules


def _add_business_info(store_db: dict) -> str:
    return f"""\nYour name is {store_db['ai_name']}. Your personality: {store_db['ai_behavior']}. \
    Your Age: {store_db['ai_age']}. Your Gender: {store_db['ai_gender']}. Business Name: {store_db['business_name']}.
    Business Type: {store_db['business_type']}. Business Description: {store_db['description']}."""


def _format_business_hours(opentime: dict) -> str:
    hours = []
    for day, time in opentime.items():
        if isinstance(time, dict) and time.get('open'):
            hours.append(f"{day}: {time['from']} - {time['to']}")
    return ", ".join(hours)


def _clean_prompt(prompt: str) -> str:
    """Clean the prompt by removing unnecessary characters."""
    return re.sub(r'(?<=\n)(\s+)', '', prompt)


def _add_product_info(store_db: dict) -> str:
    product_info = "\n\nHere's your product list:"
    for product in store_db['product']:
        product_info += f"\n- {product['name']} {product['description']} {product['price']}"
    return product_info


def _product_list(self, page_id: str) -> str:
    """Get product list from database"""
    store_db = self.get_db_data(page_id)
    try:
        return "\n".join(
            [f"- {product['name']} {product['description']} {product['price']}" for product in store_db['product']])
    except Exception as e:
        logging.error(e)
        return "No product found"


