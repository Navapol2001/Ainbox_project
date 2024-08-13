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
    return """\n- You cannot receive an order from the user and process it.
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
    return f"""\nWhen responding, MUST output a response in one of two formats:
\n**Option 1:**\nUse this if you want the human to use a tool.\n
```json
\n
{{\n
    "answer_response": string,\n
    "topic": string,\n
    "customer_feeling": string,\n
    "action": string,\n
    "args": dict\n
}}\n```\n
**Option #2:**\nUse this if you want to respond directly to the human.\n
```json\n
    {{\n
        "answer_response": string,\n
        "topic": string,\n
        "action": "direct_response",\n
        "customer_feeling": string,\n
        "answer_able": bool\n
        }}\n
        ```\n
        """


def _add_rules(rank: str) -> str:
    rules = """\nStrict Rules:\n
    - If user asks you a question unrelated to our business, **politely decline.**\n
    - **Stay Within Your Boundaries:**  If a customer asks a question outside of scope, politely inform them that \
    you can't answer that.
    - Keep responses **short **\n
    - **Stick to the facts** about our products and services. Don't make anything up.\n
    - **Concise answers** are best. \n
    - **No unnecessary emojis.**\n
    - **Always follow** our product and business information precisely.\n
    - For questions that require human assistance\n
    """
    if rank == "EC1":
        rules += _add_rank1_rules()
    else:
        rules += _add_rank2_rules()
    return rules


def _add_business_info(store_db: dict) -> str:
    return f"""\nYour name is {store_db['ai_name']}. Your personality: {store_db['ai_behavior']}. \
    Your Age: {store_db['ai_age']}. Your Gender: {store_db['ai_gender']}. Business Name: {store_db['business_name']}.
    Business Type: {store_db['business_type']}. Business Description: {store_db['description']}.
    Business Address: {store_db['address']['detailedAddress']}, {store_db['address']['subdistrict']},
    {store_db['address']['district']}, {store_db['address']['province']}, Zipcode: {store_db['address']['zipcode']}
     Business Phone Number: {store_db['phone']}. Business Email: {store_db['email']}.
     Business Website: {store_db['website']}. Business Hours: {_format_business_hours(store_db['opentime'])}"""


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


class Information_page(db_connect):
    def __init__(self):
        super().__init__()

    def generate_admin_prompt(self, page_id: str, rank: str) -> str:
        """
        Generate a prompt template for the admin.

        Args:
            page_id (str): The ID of the page.
            rank (int): The version of the template to use.

        Returns:
            str: The generated prompt template.
        """
        store_db = self.get_db_data(page_id)
        prompt_text = self._build_prompt_text(store_db, rank)
        return _clean_prompt(prompt_text)

    def _build_prompt_text(self, store_db: dict, rank: str) -> str:
        prompt_text = f"""You are now the "Admin Page" of {store_db['business_name']}. 
        Your mission is to provide accurate and helpful information to customers. """
        prompt_text += f"""By providing excellent customer service and adhering to these rules,
        you're helping {store_db['business_name']} succeed."""
        prompt_text += _add_business_info(store_db)
        prompt_text += _add_rules(rank)
        prompt_text += _example_()
        return prompt_text


class Ecommerce_page(db_connect):
    def __init__(self):
        super().__init__()

    def generate_admin_prompt(self, page_id: str, rank: str) -> str:
        """
        Generate a prompt template for the admin.

        Args:
            page_id (str): The ID of the page.
            rank (str): The version of the template to use.

        Returns:
            str: The generated prompt template.
        """
        store_db = self.get_db_data(page_id)
        prompt_text = self._build_prompt_text(store_db, rank)
        return _clean_prompt(prompt_text)

    def _build_prompt_text(self, store_db: dict, rank: str) -> str:
        prompt_text = f"""You are now the "Admin Page" of {store_db['business_name']}. 
        Your mission is to provide accurate and helpful information to customers. """
        prompt_text += f"""By providing excellent customer service and adhering to these rules, 
        you're helping {store_db['business_name']} succeed."""
        prompt_text += _add_business_info(store_db)
        prompt_text += _add_product_info(store_db)
        prompt_text += _add_rules(rank)
        prompt_text += _example_()
        return prompt_text

    # def order_tools(self) -> str:
    #     """Get all tools for order"""
    #     return """{
    #         "name": "order_data",
    #         "description": "Use this tool for creating orders for users, storing order data in the database.",
    #         "args": {
    #             "customer_name": "customer_name",
    #             "customer_last_name": "customer_last_name",
    #             "customer_address": "customer_address",
    #             "customer_sub_district": "customer_sub_district",
    #             "customer_district": "customer_district",
    #             "customer_provinces": "customer_provinces",
    #             "customer_country": "customer_country",
    #             "customer_zip": "customer_zip",
    #             "customer_phone": "customer_phone",
    #             "customer_email": "customer_email",
    #             "product_name": "product_name",
    #             "product_quantity": "product_quantity"
    #         }
    #     }"""
