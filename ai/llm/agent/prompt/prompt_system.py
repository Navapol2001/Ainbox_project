from pymongo import MongoClient
import os
import re
import logging
import dotenv

dotenv.load_dotenv()

class db_connect:
    def __init__(self):
        self.client = MongoClient(os.environ.get('MONGO_DB_URI'))

class Information_page(db_connect):
    def __init__(self):
        super().__init__()        

    def generate_admin_prompt(self, page_id: str, rank: int) -> str:
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
        return self.clean_prompt(prompt_text)

    def _build_prompt_text(self, store_db: dict, rank: int) -> str:
        prompt_text = f"""You are now the "Admin Page" of {store_db['business_name']}. Your mission is to provide accurate and helpful information to customers. """
        prompt_text += f"""By providing excellent customer service and adhering to these rules, you're helping {store_db['business_name']} succeed."""
        prompt_text += self._add_business_info(store_db)
        prompt_text += self._add_rules(rank)
        prompt_text += self._example_()
        return prompt_text

    def _add_business_info(self, store_db: dict) -> str:
        return f"""\nYour name is {store_db['ai_name']}. Your personality: {store_db['ai_behavior']}. Your Age: {store_db['ai_age']}. Your Gender: {store_db['ai_gender']}. Business Name: {store_db['business_name']}. Business Type: {store_db['business_type']}. Business Description: {store_db['description']}. Business Address: {store_db['address']['detailedAddress']}, {store_db['address']['subdistrict']}, {store_db['address']['district']}, {store_db['address']['province']}, Zipcode: {store_db['address']['zipcode']}. Business Phone Number: {store_db['phone']}. Business Email: {store_db['email']}. Business Website: {store_db['website']}. Business Hours: {self._format_business_hours(store_db['opentime'])}"""

    def _format_business_hours(self, opentime: dict) -> str:
        hours = []
        for day, time in opentime.items():
            if isinstance(time, dict) and time.get('open'):
                hours.append(f"{day}: {time['from']} - {time['to']}")
        return ", ".join(hours)

    def _add_rules(self, rank: int) -> str:
        rules = f"""\nStrict Rules:\n
        - If user asks you a question unrelated to our business, **politely decline.**\n
        - **Stay Within Your Boundaries:**  If a customer asks a question outside of scope, politely inform them that you can't answer that.
        - Keep responses **short **\n
        - **Stick to the facts** about our products and services. Don't make anything up.\n
        - **Concise answers** are best. \n
        - **No unnecessary emojis.**\n
        - **Always follow** our product and business information precisely.\n
        - For questions that require human assistance\n
        """
        if rank == 1:
            rules += self._add_rank1_rules()
        else:
            rules += self._add_rank2_rules()
        return rules

    def _add_rank1_rules(self) -> str:
        return """\n- You cannot receive an order from the user and process it.
    \nWhen responding, MUST output a response in this format:
    
    \n```json\n
        {\n
        "answer_response": string, \ You should put what you want to return to use here
        "topic": string, \ The topic of the conversation. Must be one of consult, order , complaint , general , product , other
        "action": "direct_response", \ Must be "direct_response
        "customer_feeling": string, \ The feeling of the customer must be one of (happy, sad, angry, neutral)
        "answer_able : int \ 1 = Able to answer within given context ,0 = if cannot answer within context , call for human 
        \n}
        \n```"""

    def _add_rank2_rules(self) -> str:
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

    def _example_(self) -> str:
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

    def get_db_data(self, page_id: str) -> dict:
        """Get store data from database"""
        filter = {'page_id': page_id}
        store_db = self.client['AI_Chat']['store_db'].find_one(filter)
        if store_db:
            return store_db['details']
        else:
            raise ValueError("No data found for the given page_id")

    def clean_prompt(self, prompt: str) -> str:
        """Clean the prompt by removing unnecessary characters."""
        return re.sub(r'(?<=\n)(\s+)', '', prompt)

# The Ecommerce_page class remains the same as in the previous response

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
        return self.clean_prompt(prompt_text)

    def _build_prompt_text(self, store_db: dict, rank: str) -> str:
        prompt_text = f"""You are now the "Admin Page" of {store_db['business_name']}. Your mission is to provide accurate and helpful information to customers. """
        prompt_text += f"""By providing excellent customer service and adhering to these rules, you're helping {store_db['business_name']} succeed."""
        prompt_text += self._add_business_info(store_db)
        prompt_text += self._add_product_info(store_db)
        prompt_text += self._add_rules(rank)
        prompt_text += self._example_()
        return prompt_text

    def _add_business_info(self, store_db: dict) -> str:
        return f"""\nYour name is {store_db['ai_name']}. Your personality: {store_db['ai_behavior']}. Your Age: {store_db['ai_age']}. Your Gender: {store_db['ai_gender']}. Business Name: {store_db['business_name']}. Business Type: {store_db['business_type']}. Business Description: {store_db['description']}. Business Address: {store_db['address']['detailedAddress']}, {store_db['address']['subdistrict']}, {store_db['address']['district']}, {store_db['address']['province']}, Zipcode: {store_db['address']['zipcode']}. Business Phone Number: {store_db['phone']}. Business Email: {store_db['email']}. Business Website: {store_db['website']}. Business Hours: {self._format_business_hours(store_db['opentime'])}"""

    def _format_business_hours(self, opentime: dict) -> str:
        hours = []
        for day, time in opentime.items():
            if isinstance(time, dict) and time.get('open'):
                hours.append(f"{day}: {time['from']} - {time['to']}")
        return ", ".join(hours)

    def _add_product_info(self, store_db: dict) -> str:
        product_info = "\n\nHere's your product list:"
        for product in store_db['product']:
            product_info += f"\n- {product['name']} {product['description']} {product['price']}"
        return product_info

    def _add_rules(self, rank: str) -> str:
        rules = """\nStrict Rules:\n
        - If user asks you a question unrelated to our business, **politely decline.**\n
        - **Stay Within Your Boundaries:**  If a customer asks a question outside of scope, politely inform them that you can't answer that.
        - Keep responses **short **\n
        - **Stick to the facts** about our products and services. Don't make anything up.\n
        - **Concise answers** are best. \n
        - **No unnecessary emojis.**\n
        - **Always follow** our product and business information precisely.\n
        - For questions that require human assistance\n
        """
        if rank == "EC1":
            rules += self._add_rank1_rules()
        else:
            rules += self._add_rank2_rules()
        return rules

    def _add_rank1_rules(self) -> str:
        return """\n- You cannot receive an order from the user and process it.
    \nWhen responding, MUST output a response in this format:
    
    \n```json\n
        {\n
        "answer_response": string, \ You should put what you want to return to use here
        "topic": string, \ The topic of the conversation. Must be one of consult, order , complaint , general , product , other
        "action": "direct_response", \ Must be "direct_response
        "customer_feeling": string, \ The feeling of the customer must be one of (happy, sad, angry, neutral)
        "answer_able : int \ 1 = Able to answer within given context ,0 = if cannot answer within context , call for human 
        \n}
        \n```"""

    def _add_rank2_rules(self) -> str:
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
            Your tools: {self.order_tools()}
            """

    def _example_(self) -> str:
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

    def product_list(self, page_id: str) -> str:
        """Get product list from database"""
        store_db = self.get_db_data(page_id)
        try:
            return "\n".join([f"- {product['name']} {product['description']} {product['price']}" for product in store_db['product']])
        except Exception as e:
            logging.error(e)
            return "No product found"

    def get_db_data(self, page_id: str) -> dict:
        """Get store data from database"""
        filter = {'page_id': page_id}
        store_db = self.client['AI_Chat']['store_db'].find_one(filter)
        if store_db:
            return store_db['details']
        else:
            raise ValueError("No data found for the given page_id")

    def order_tools(self) -> str:
        """Get all tools for order"""
        return """{
            "name": "order_data",
            "description": "Use this tool for creating orders for users, storing order data in the database.",
            "args": {
                "customer_name": "customer_name",
                "customer_last_name": "customer_last_name",
                "customer_address": "customer_address",
                "customer_sub_district": "customer_sub_district",
                "customer_district": "customer_district",
                "customer_provinces": "customer_provinces",
                "customer_country": "customer_country",
                "customer_zip": "customer_zip",
                "customer_phone": "customer_phone",
                "customer_email": "customer_email",
                "product_name": "product_name",
                "product_quantity": "product_quantity"
            }
        }"""

    def clean_prompt(self, prompt: str) -> str:
        """Clean the prompt by removing unnecessary characters."""
        return re.sub(r'(?<=\n)(\s+)', '', prompt)


