import asyncio
from datetime import datetime, timedelta
import logging 
import os 
from typing import List, Optional

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.enums import ParseMode
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from admin import admin_only
from models import MessageRecord, Category, User, ActiveSubscription, Session
from sqlalchemy.orm import Session as S
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def send_last_3_days_messages(bot: Bot, user_id: int, category_id:int):
    session = Session()
    try:
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        messages = session.query(MessageRecord).filter(
            MessageRecord.category_id == category_id,
            MessageRecord.date >= three_days_ago
        ).order_by(MessageRecord.date).all()

        for message in messages():
            try:
                message_text = (
                        f"{message.text}\n\n"
                        f"От: {message.sender_name}"
                )
                if message.sender_username:
                    message_text += f", @{message.sender_username}"
                message_text += f"\nЧат: {message.chat_title}"
                
                # Include the message link if available
                if message.message_link:
                    message_text += f"\nСсылка: {message.message_link}"

                await bot.send_message(
                    chat_id=user_id,
                    text=message_text,
                    parse_mode=ParseMode.HTML   
                )

            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")

    except Exception as e:
        logger.error(f"Error retrieving messages: {e}")
    finally:
        session.close()



async def handle_expired_subscription(bot: Bot, user: User, category: Category, session:S):
    try:
        await bot.send_message(
            chat_id=user.chat_id,
            text=f"Ваша подписка на категорию '{category.name}' истекла. "
                 f"Для продления подписки, пожалуйста, обратитесь к боту."
        )
        # Delete expired subscription
        active_sub = session.query(ActiveSubscription).filter(
            ActiveSubscription.user_id == user.id,
            ActiveSubscription.category_id == category.id
        ).first()
        if active_sub:
            session.delete(active_sub)
            session.commit()
    except Exception as e:
        logging.error(f"Error handling expired subscription for user {user.id}: {e}")

# async def start_category_bot(category: Category):

#     logger.debug("category_started")
#     if hasattr(category, 'bot_token') and category.bot_token:
#         bot = Bot(token=category.bot_token)
#     else:
#         return None
#     router = Router(name=f"category_bot_{category.id}")

#     @router.message(CommandStart())
#     async def handle_start(message: Message):
#         print("start trigerred")
#         user_id = message.from_user.id
#         session = Session()
#         try:
#             subscription = session.query(ActiveSubscription).join(User).filter(
#                 User.chat_id == user_id,
#                 ActiveSubscription.category_id == category.id
#             ).first()

#             current_time = datetime.utcnow()

#             if subscription:
#                 if subscription.end_date <= current_time:
#                     # Subscription expired - delete and notify
#                     await handle_expired_subscription(bot, subscription.user, category, session)
#                     await message.answer("Ваша подписка истекла. Для продления подписки, пожалуйста, обратитесь к боту.")
#                 else:
#                     # Active subscription
#                     await send_last_3_days_messages(bot, user_id, category.id)
#             else:
#                 await message.answer("У вас нет активной подписки на эту категорию.")
#         except Exception as e:
#             logging.error(f"Error in welcome message: {e}")
#         finally:
#             session.close()

#     return router
        
def run_bot(category:Category):
    if not hasattr(category, 'bot_toeken') or not category.bot_token:
        logger.warning("fCategory {category.id} does not have a valid bot token. Skipping...")
        return
    
    bot = Bot(token=Category.bot_token)
    router = Router(name=f"category_bot_{category.id}")


    @router.message(CommandStart())
    async def handle_start(message:Message):
        user_id = message.from_user.id
        logger.debug("fReceived /start command from user {user_id} for helper bot {category.id}")
        

        with Session() as session:
            try:
                subscription = await session.execute(
                    session.query(ActiveSubscription)
                    .join(User)
                    .filter(
                        User.chat_id == user_id,
                        ActiveSubscription.category_id == category.id
                    )
                ).scalar_one_or_none()

                current_time = datetime.utcnow()

                if subscription:
                    if subscription.end_date <= current_time:
                        await handle_expired_subscription(bot, subscription.user, category, session)
                        await message.answer("Ваша подписка кончилась пожалуйста обновите ее")
                    else:
                        await send_last_3_days_messages(bot, user_id, category.id)
                else:
                    await message.answer("Пожалуйста купите подписку на категорию в нашем боте чтобы получать последние фриланс предложения")
            except Exception as e:
                logger.error(f"Error handling /start command: {e}")
            finally:
                await session.close()

        async def start_polling():
            dp = Dispatcher()
            dp.include_router(router)
            logger.info(f"Starting polling for helper bot {category.id}...")
            await dp.start_polling(bot)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_polling())


async def distribute_message(message_data: dict, categories: list[Category], main_bot: Bot):
    session = Session()
    try:
        current_time = datetime.utcnow()
       
        for category in categories:
            # Reattach the category to this session and eager load active subscriptions
            category = session.merge(category)
            session.refresh(category, ['active_subscriptions'])
           
            # Get all active subscriptions
            active_subscriptions = session.query(ActiveSubscription).filter(
                ActiveSubscription.category_id == category.id
            ).all()

            # Process each subscription
            for subscription in active_subscriptions:
                user = subscription.user

                # Check if subscription has expired
                if subscription.end_date <= current_time:
                    # Handle expired subscription - delete and notify
                    sending_bot = Bot(token=category.bot_token) if category.bot_token else main_bot
                    await handle_expired_subscription(sending_bot, user, category, session)
                    if sending_bot != main_bot:
                        await sending_bot.session.close()
                    continue

                # Prepare message text for active subscriptions
                message_text = (
                    f"Новое сообщение в категории '{category.name}':\n\n"
                    f"{message_data['text']}\n\n"
                    f"От: {message_data['sender_name']}"
                )
                if message_data['sender_username']:
                    message_text += f", @{message_data['sender_username']}"
                message_text += f"\nЧат: {message_data['chat_title']}"
               
                if 'message_link' in message_data and message_data['message_link']:
                    message_text += f"\nСсылка: {message_data['message_link']}"

                # Determine which bot to use
                sending_bot = None
                if category.bot_token:
                    try:
                        sending_bot = Bot(token=category.bot_token)
                    except Exception as e:
                        logging.error(f"Error initializing category bot: {e}")
                        sending_bot = main_bot
                else:
                    sending_bot = main_bot

                # Send message
                try:
                    await sending_bot.send_message(
                        chat_id=user.chat_id,
                        text=message_text
                    )
                except Exception as e:
                    logging.error(f"Failed to send message to user {user.id}: {e}")
                finally:
                    # Close category bot if it was created
                    if sending_bot != main_bot:
                        await sending_bot.session.close()

    except Exception as e:
        logging.error(f"Error in distribute_message: {e}")
        session.rollback()
    finally:
        session.close()


distribution_router = Router(name="distribution_router")


# async def setup_existing_bots():
#     session = Session()
#     print("started setup")
#     try:
#         categories = session.query(Category).filter(Category.bot_token.isnot(None)).all()
#         routers = []
#         for category in categories:
#             category_router = await start_category_bot(category)
#             print(category_router)
#             if category_router:
#                 routers.append(category_router)
#         return routers
#     finally:
#         session.close()


def get_distribution_router() -> Router:
    return distribution_router