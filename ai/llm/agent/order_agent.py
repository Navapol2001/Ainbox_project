from .model import model_base,transform_function

class order_agent(model_base):
    def __init__(self):

        tools_list = [StoreRetailFn().order_data]
        super().__init__(tools_list)  # Call the parent class's __init__
        self.tool_caller = self.model  # Store the model object directly
        self.t_fn = transform_function()
        self.tools_process = StoreRetailFn()
        self.prompt = PromptGenerator()

    def order(self, received ,page_id):
        # Use the model and tools separately
        chat = self.tool_caller.start_chat()
        product_list = self.prompt.product_list(page_id)
        response = chat.send_message(
            f"Extract message data to create an order message:{received}\
                Following These available product :\
                    {product_list}",tool_config={'function_calling_config':'ANY'}) 
        if 'function_call' in response.candidates[0].content.parts[0]:
            arg_json = self.t_fn.fn_to_args(response)
            try :
                tool_excute = self.tools_process.order_data(**arg_json['args'])
                return tool_excute
            except Exception as e:
                return e
        else:
            return False

