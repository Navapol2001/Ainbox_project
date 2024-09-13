
from llm.db import db_connect
from .prompt_system import _clean_prompt, _add_business_info, _add_rules, _example_



class Information(db_connect):
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
        return prompt_text
