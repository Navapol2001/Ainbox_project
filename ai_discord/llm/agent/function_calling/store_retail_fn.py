import pymongo
import os
from dotenv import load_dotenv
load_dotenv()

class StoreRetailFn:
    def __init__(self):
        self.myclient = pymongo.MongoClient(os.getenv("MONGO_DB_URI"))
        self.mydb = self.myclient["AI_Chat"]
        self.mycol = self.mydb["order_db"]

    def order_data(self, 
                    product_name: str, 
                    product_quantity: int, 
                    customer_name: str, 
                    customer_last_name: str, 
                    customer_phone: str, 
                    customer_email: str, 
                    customer_address: str, 
                    customer_sub_district: str ,
                    customer_district : str ,
                    customer_provinces: str ,
                    customer_country: str ,
                    customer_zip: str ):
        """
        Use this tool for create order for user, this tool will store the order data in the database.
        Args:
            product_name (str) | None: product name
            product_quantity (int) | None: product quantity
            customer_name (str) | None: customer first name
            customer_last_name (str) | None: customer last name
            customer_phone (str) | None: customer phone number
            customer_email (str) | None: customer email
            customer_address (str) | None: customer address
            customer_sub_district (str) | None: customer sub district
            customer_district (str) | None: customer district
            customer_provinces (str) | None: customer provinces
            customer_country (str) | None: customer country
            customer_zip (str) | None: customer zip code
            if data is not sure or unknown, or if data is missing:
                use None
            else:
                ensure all data is valid and accurate before proceeding
    Returns:
            str: A message indicating the status of the order request.
        """
        dict_item = {
            "customer_last_name": customer_last_name,
            "customer_address": customer_address,
            "customer_sub_district": customer_sub_district,
            "customer_district": customer_district,
            "customer_provinces": customer_provinces,
            "customer_country": customer_country,
            "customer_zip": customer_zip,
            "customer_phone": customer_phone,
            "customer_email": customer_email,
            "product_name": product_name,
            "product_quantity": product_quantity,
        }
        if any(val == "unknown" or val is None or val == "None" for val in [product_name, product_quantity, customer_name, customer_last_name, customer_address, customer_phone, customer_email, customer_sub_district, customer_provinces, customer_country, customer_zip ,customer_district]):
            missing_value = list(filter(lambda x: x[1] == "unknown" or x[1] is None, dict_item.items()))

            return f"System: Please provide the following values: {missing_value}"

        data = {
            "product_name": product_name,
            "product_quantity": product_quantity,
            "customer_name": customer_name,
            "customer_last_name": customer_last_name,
            "customer_address": customer_address,
            "customer_phone": customer_phone,
            "customer_email": customer_email,
            "customer_sub_district": customer_sub_district,
            "customer_district": customer_district,
            "customer_provinces": customer_provinces,
            "customer_country": customer_country,
            "customer_zip": customer_zip,
        }

        self.mycol.insert_one(data)
        return "System: Order Request Successful. Your order will be confirmed soon."
