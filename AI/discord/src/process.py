import asyncio
import logging
import os
from datetime import datetime as time


from .message import MessageSender
from .user_check import QuotaCheck, tier

# Initialize classes
msg = MessageSender()
quota = QuotaCheck()
tier = tier()


async def process_adapter(data: dict[str, str]) -> str:
    """
    Processes incoming messages, checks quotas and user status, 
    and sends responses accordingly.

    Args:
        data (dict): A dictionary containing message details.

    Returns:
        str: A message indicating the result of the processing.
    """

    message = data['msg']
    user_id = data['user_name']
    server_name = data['server_name']

    check_status = await quota.check_status(page_id=server_name)
    check_quota = await quota.check_quota(server_name)
    rank = await tier.get_tier(page_id=server_name)

    if not check_status:
        logging.info("Bot is inactive")
        msg.bot_inactive_react(
            method='line',
            user_id=user_id,
            message=message,
            time_stamp=time.now(),
            page_id=server_name
        )
        return "Bot is inactive / No Service for Your Server"
    
    if check_quota:
        result_msg = await msg.send_message_discord(
            user_id=user_id,
            message=message,
            time_stamp=time.now(),
            page_id=server_name,
            rank=rank
        )
        await quota.decrease_quota(server_name)
        return result_msg['answer']
    else:
        logging.info("Quota limit reached")
        msg.bot_inactive_react(
            method='discord',
            message=message,
            user_id=user_id,
            time_stamp=time.now(),
            page_id=server_name
        )
        return "Quota limit reached"
    