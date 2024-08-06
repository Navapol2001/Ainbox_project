import google.generativeai as genai 
import os 
import dotenv
dotenv.load_dotenv()
import json

class model_base:
    def __init__(self,tools):
        genai.configure(api_key=os.environ['MODEL_API_KEY'])
        self.model = genai.GenerativeModel("gemini-1.5-flash",tools=tools)

class transform_function:
    def __init__(self):
        pass
    def fn_to_args(self,response):
        fn=response.candidates[0].content.parts[0].function_call
        arg = json.dumps(type(fn).to_dict(fn), indent=4)
        arg_json = json.loads(arg)
        return arg_json

