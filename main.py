import asyncio
import os
from threading import Thread
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, joinedload
from categories import CATEGORIES
from models import Category, MessageRecord, User, ReferralData
from models import Base, engine
from referals import generate_referral_code, cmd_referral_stats
from auth import telethon_router
from dotenv import load_dotenv
from admin import router_admin
import logging
import re
from categories import router_categories
from utils import router_utils, useful_info, support_chat, setup_message_retention
from datetime import datetime
from subscriptions import router_subscriptions
from message_broadcaster import router_broadcast
import redis 
import json
from bots import distribute_message, get_distribution_router, run_bot, start_new_bot, running_bots
logging.basicConfig(level=logging.INFO)





load_dotenv()

MAIN_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(MAIN_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

if "AMVERA" in os.environ:
    r = redis.Redis(host='amvera-salyev-run-freelance-bot-redis', port=6379, db=0)
else:
    r = redis.Redis(host='localhost', port=6379, db=0)

Session = sessionmaker(bind=engine)

dp.include_router(router_categories)
dp.include_router(router_utils)
dp.include_router(router_subscriptions)
dp.include_router(telethon_router)
dp.include_router(router_broadcast)
dp.include_router(router_admin)
WELCOME_MESSAGE = """Привет! Ты активировал Golubin bot. Бот
ежедневно присылает более 100 заявок на
услуги фриланса.
📌 «Категории заявок>» - выбор
категории по которой будут приходить
заявки, можешь выбрать нужную
категорию и попробовать ее в деле
📌 «Реферальная система» - дает твою
личную реферальную ссылку. Отправь ее
друзьям для регистрации и с каждой
оплаты будешь получать до 50% на свой
счет. Эти деньги можно вывести или
оплатить категорию заявок
📌 «Полезное» - много полезных статей
по использованию бота.
📌 «Разместить объявление» -
разместить объявление в боте о поиске
специалиста
📌 «Техподдержка» - можно задать
любой вопрос по работе бота.
📌 "Заказать направление" - если
вашего направления нет в "Категории заявок", 
то можете заказать его разработку"""



WELCOME_MESSAGE_REGISTERED = '''
«🤑Категории заявок» - выбор
категории по которой будут приходить
заявки, можешь выбрать нужную
категорию и попробовать ее в деле
запросив заявки за прошедшие сутки

«⭐️ Полезное» - много полезных статей
по использованию бота

«⚙️ Техподдержка» - можно задать
любой вопрос по работе бота

«🤝 Партнерская витрина» - Различные бонусы для клиентов бота от наших партнеров

«👤 Личный кабинет» - подписки, стоп слова, реф система, аккаунты и многое другое

«➕ Доп услуги» - размещение объявлений, добавление чатов для перессылки, заказ нового направления'''






keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🤑 Категории заявок"),
            KeyboardButton(text="💵 Реферальная система"),
        ],
        [
            KeyboardButton(text="⭐️ Полезное"),
            KeyboardButton(text="⬆️ Разместить объявление"),
        ],
        [
            KeyboardButton(text="⚙️ Техподдержка"),
            KeyboardButton(text="📝Заказать направление"),
        ],
    ],
    resize_keyboard=True,
    is_persistent=True
)

keyboard_registered = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🤑 Категории заявок"),
            KeyboardButton(text="⭐️ Полезное"),
        ],
        [
            KeyboardButton(text="⚙️ Техподдержка"),
            KeyboardButton(text="🤝Партнерская витрина")
        ],
        [
            KeyboardButton(text="👤 Личный кабинет"),
            KeyboardButton(text="➕Доп услуги")
        ]
        
    ],
    resize_keyboard=True,
    is_persistent=True
)


keyboard_personal_cabinet = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text="✅ Мои подписки"),
            KeyboardButton(text="⛔️ Стоп слова ⛔️")
        ],
        [
            KeyboardButton(text="💵 Реферальная система"),
            KeyboardButton(text="👥 Аккаунты"),
        ],
        [
            KeyboardButton(text="📊 Статистика"),
            KeyboardButton(text="📋 Гугл таблицы")
        ],
        [
            KeyboardButton(text="В главное меню")
        ]
    ],
    resize_keyboard=True
)



def create_categories_keyboard():
    keyboard_inline = []
    for i, category in enumerate(CATEGORIES):
        keyboard_inline.append([InlineKeyboardButton(text=category, callback_data=f"cat_{i}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard_inline)







# async def process_message(event):
#     session = Session()
#     try:
#         message_text = event.message.text or ""
#         categories = session.query(Category).all()
#         matched_categories = []
#         for category in categories:
#             matched_keyword = message_matches_category(message_text, category)
#             if matched_keyword:
#                 sender = await event.get_sender()
#                 chat = await event.get_chat()
#                 new_message = MessageRecord(
#                     chat_id=chat.id,
#                     chat_title=getattr(chat, 'title', None),
#                     message_id=event.message.id,
#                     sender_id=sender.id if sender else None,
#                     sender_name=getattr(sender, 'first_name', 'Unknown User'),
#                     sender_username=getattr(sender, 'username', None),
#                     text=message_text,
#                     date=event.message.date,
#                     category_id=category.id,
#                     matched_keyword=matched_keyword
#                 )
#                 session.add(new_message)
#                 matched_categories.append(category)
       
#         if matched_categories:
#             session.commit()
#             await distribute_message(event, matched_categories)
#     finally:
#         session.close()


# async def distribute_message(event, categories: list[Category]):
#     session = Session()
#     try:
#         current_time = datetime.utcnow()
       
#         for category in categories:
#             category = session.merge(category)
#             session.refresh(category, ['active_subscriptions'])
           
#             active_subscriptions = [
#                 sub for sub in category.active_subscriptions
#                 if sub.end_date > current_time
#             ]
#             for subscription in active_subscriptions:
#                 user = subscription.user
#                 sender = await event.get_sender()
#                 chat = await event.get_chat()
#                 sender_name = getattr(sender, 'first_name', 'Unknown User')
#                 username = getattr(sender, 'username', None)
#                 sender_info = f"{sender_name} (@{username})" if username else sender_name
                
#                 await bot.send_message(
#                     chat_id=user.chat_id,
#                     text=f"New message in category '{category.name}':\n\n"
#                             f"{event.message.text}\n\n"
#                             f"From: {sender_info}\n"
#                             f"Chat: {getattr(chat, 'title', 'Unknown Chat')}"
#                     )
                
#     finally:
#         session.close()



# def message_matches_category(message_text: str, category: Category) -> str | None:
#     keywords = [kw.strip() for kw in category.keywords.split(',')]
#     message_text_lower = message_text.lower()
   
#     for keyword in keywords:
#         keyword_lower = keyword.lower()
#         is_hashtag = keyword.startswith('#')
#         if is_hashtag:
#             keyword_lower = keyword_lower[1:]
        
#         keyword_parts = keyword_lower.split()
        
#         word_patterns = [rf'\b{re.escape(word)}\w*' for word in keyword_parts]
        
#         if is_hashtag:
#             pattern = r'#' + r'\s+'.join(word_patterns)
#         else:
#             pattern = r'\s+'.join(word_patterns)
        
#         if re.search(pattern, message_text_lower):
#             return keyword  
   
#     return None

# def message_matches_category(message_text: str, category: Category) -> str | None:
#     keywords = category.keywords.split(',')
#     message_text_lower = message_text.lower()
    
#     for keyword in keywords:
#         keyword = keyword.strip().lower()
#         is_hashtag = keyword.startswith('#')

#         if is_hashtag:
#             keyword = keyword[1:]
#         pattern = r'\b' + re.escape(keyword) + r'\w*\b'
        
#         if is_hashtag:
#             hashtag_pattern = r'#' + pattern
#             if re.search(hashtag_pattern, message_text_lower):
#                 return '#' + keyword  
        
#         if re.search(pattern, message_text_lower):
#             return '#' + keyword if is_hashtag else keyword
    
#     return None
        





# @dp.message(Command("start"))
# async def cmd_start(message: Message):
#     session = Session()
#     user_chat_id = message.from_user.id  # or however you get the user's chat_id
#     user = session.query(User).options(joinedload(User.categories)).filter(User.chat_id == user_chat_id).first()
#     try:
#         if user:
#             if user.categories:
#                 await message.answer(WELCOME_MESSAGE_REGISTERED, reply_markup=keyboard_registered)
#             else:
#                 await message.answer(WELCOME_MESSAGE, reply_markup=keyboard)
#         else:
#             user = User(
#                 username=message.from_user.username,
#                 first_name=message.from_user.first_name,
#                 last_name=message.from_user.last_name,
#                 chat_id=message.chat.id
#             )
#             session.add(user)
#             session.commit()   
#             await message.answer(WELCOME_MESSAGE, reply_markup=keyboard)
#     finally:    
#         session.close()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    session = Session()
    try:
        user_chat_id = message.from_user.id
        user = session.query(User).options(joinedload(User.categories)).filter(User.chat_id == user_chat_id).first()
        
        referral_code = None
        if message.text:
            parts = message.text.split(maxsplit=1)
            if len(parts) > 1:
                referral_code = parts[1].strip()  # Get referral code from /start command arguments
        
        if user:
            if not user.referral_code:
                user.referral_code = generate_referral_code(session, user_chat_id)
                session.commit()
            
            if user.categories:
                await message.answer(WELCOME_MESSAGE_REGISTERED, reply_markup=keyboard_registered)
            else:
                await message.answer(WELCOME_MESSAGE, reply_markup=keyboard)
        else:
            user = User(
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                chat_id=message.chat.id,
                referral_code=generate_referral_code(session, user_chat_id)
            )
            session.add(user)
            
            # Handle referral
            if referral_code and referral_code != user.referral_code:  # Prevent self-referral
                referrer = session.query(User).filter_by(referral_code=referral_code).first()
                if referrer:
                    user.referred_by = referrer
                    referrer_data = referrer.referral_data
                    if not referrer_data:
                        referrer_data = ReferralData(user=referrer)
                        session.add(referrer_data)
                    referrer_data.activations_count += 1
                    await message.answer("Вы успешно активировали реферальную ссылку")
            
            # Create ReferralData for the new user
            user_referral_data = ReferralData(user=user)
            session.add(user_referral_data)
            
            session.commit()
            await message.answer(WELCOME_MESSAGE, reply_markup=keyboard)
    
    finally:    
        session.close()


# @dp.message(F.text == "🤑 Категории заявок")
# async def handle_categories(message: Message):
#     data = create_categories_keyboard()
#     await message.answer("Выберите категорию", reply_markup=data)



@dp.message(F.text == "💵 Реферальная система")
async def handle_referral(message: Message):
    await cmd_referral_stats(message)

@dp.message(F.text == "⭐️ Полезное")
async def handle_useful(message: Message):
    await message.answer(text="Полезное:", reply_markup=useful_info(message))

@dp.message(F.text == "⬆️ Разместить объявление")
async def handle_post_ad(message: Message):
    await message.answer("Вы выбрали размещение объявления. Здесь будет функционал для создания объявлений.")

@dp.message(F.text == "⚙️ Техподдержка")
async def handle_support(message: Message, state:FSMContext):
    await support_chat(message, state)


@dp.message(F.text == "📝Заказать направление")
async def handle_order_direction(message: Message):
    await message.answer("Вы выбрали заказ направления. Здесь будет функционал для заказа нового направления.")



PERSONAL_CABINET = '''«✅ Мои подписки» -  список твоих активных подписок, приостановка или перенос подписки

«⛔️ Стоп слова ⛔️» - добавление слов по которым не будут пересылаться сообщения

«💵 Реферальная система» - условия и реф ссылка

«👥 Аккаунты» - добавление до 3-х аккаунтов в каждом направлении*

«📊 Статистика» - скольким людям написал с каждого аккаунта*

«📋 Гугл таблицы» - выгрузка статистики в гугл таблицу*

*Доступно только при годовой подписке'''


@dp.message(F.text == "👤 Личный кабинет")
async def handle_personal_cabinet(message: Message):
    await message.answer(PERSONAL_CABINET, reply_markup=keyboard_personal_cabinet)


@dp.message(F.text == "В главное меню")
async def handle_main_menu(message: Message):
    await message.answer(WELCOME_MESSAGE_REGISTERED, reply_markup=keyboard_registered)

# @router.message(F.text)
# async def handle_message(message: Message):
#     await process_message(message)
def text_startswith(text: str):
    return lambda message: message.text and message.text.startswith(text)

# Update the handler for structured messages
# @dp.message(text_startswith("New message data:"))
# async def handle_structured_message(message: Message):
#     try:
#         # Extract the message data from the plain text
#         message_lines = message.text.split('\n')
#         message_data = {}
#         for line in message_lines[1:]:  # Skip the "New message data:" line
#             if ':' in line:
#                 key, value = line.split(':', 1)
#                 message_data[key.strip()] = value.strip()
        
#         # Convert types as needed
#         message_data['chat_id'] = int(message_data.get('chat_id', 0))
#         message_data['sender_id'] = int(message_data.get('sender_id', 0)) if message_data.get('sender_id') != 'None' else ''
#         message_data['date'] = datetime.fromisoformat(message_data.get('date', ''))
        
#         # message_link is already a string, no need for conversion
        
#         # Log the received data for debugging
#         # logging.info(f"Received message data: {message_data}")
        
#         # Process the message
#         await process_message(message_data)
        
#         # Acknowledge receipt
#         await message.reply("Сообщение обработано успешно")
        
#     except ValueError as ve:
#         logging.error(f"Error parsing message data: {str(ve)}")
#         await message.reply("Error processing message: Invalid data format")
#     except Exception as e:
#         logging.error(f"Error processing message: {str(e)}")
#         await message.reply("Error processing message. Please try again later.")



async def receive_messages():
    while True:
        message = r.brpop('message_queue', timeout=1)
        if message:
            _, data = message
            message_data = json.loads(data.decode('utf-8'))
            await process_message(message_data)
        await asyncio.sleep(0.1)


async def process_message(message_data: dict):
    try:
        session = Session()
        categories = session.query(Category).all()
        matched_categories = []
        for category in categories:
            matched_keyword = message_matches_category(message_data['text'] or "", category)
            if matched_keyword:
                new_message = MessageRecord(
                    chat_id=message_data['chat_id'],
                    chat_title=message_data['chat_title'],
                    message_link=message_data['message_link'],
                    sender_id=message_data['sender_id'],
                    sender_name=message_data['sender_name'],
                    sender_username=message_data['sender_username'],
                    text=message_data['text'] or "",
                    date=datetime.fromisoformat(message_data['date']),
                    category_id=category.id,
                    matched_keyword=matched_keyword
                )
                session.add(new_message)
                matched_categories.append(category)
       
        if matched_categories:
            session.commit()
            await distribute_message(message_data, matched_categories, bot)
    except Exception as e:
        logging.error(f"Error in process_message: {str(e)}")
        session.rollback()
    finally:
        session.close()






# async def distribute_message(message_data: dict, categories: list[Category]):
#     session = Session()
#     try:
#         current_time = datetime.utcnow()
       
#         for category in categories:
#             # Reattach the category to this session and eager load active subscriptions
#             category = session.merge(category)
#             session.refresh(category, ['active_subscriptions'])
           
#             # Filter for active subscriptions
#             active_subscriptions = [
#                 sub for sub in category.active_subscriptions
#                 if sub.end_date > current_time
#             ]
#             for subscription in active_subscriptions:
#                 user = subscription.user
#                 try:
#                     message_text = (
#                         f"Новое сообщение в категории '{category.name}':\n\n"
#                         f"{message_data['text']}\n\n"
#                         f"От: {message_data['sender_name']}"
#                     )
#                     if message_data['sender_username']:
#                         message_text += f", @{message_data['sender_username']}"
#                     message_text += f"\nЧат: {message_data['chat_title']}"
                    
#                     # Include the message link if available
#                     if 'message_link' in message_data and message_data['message_link']:
#                         message_text += f"\nСсылка: {message_data['message_link']}"
                    
#                     await bot.send_message(
#                         chat_id=user.chat_id,
#                         text=message_text
#                     )
#                 except Exception as e:
#                     logging.error(f"Failed to send message to user {user.id}: {e}")
#     except Exception as e:
#         logging.error(f"Error in distribute_message: {e}")
#     finally:
#         session.close()


def message_matches_category(message_text: str, category: Category) -> str | None:
    keywords = category.keywords.split('\n')
    message_text_lower = message_text.lower()
    for keyword in keywords:
        keyword = keyword.strip().lower()
        is_hashtag = keyword.startswith('#')

        if is_hashtag:
            keyword = keyword[1:]
        pattern = r'\b' + re.escape(keyword) + r'\w*\b'
        
        if is_hashtag:
            hashtag_pattern = r'#' + pattern
            if re.search(hashtag_pattern, message_text_lower):
                return '#' + keyword  
        
        if re.search(pattern, message_text_lower):
            return '#' + keyword if is_hashtag else keyword
    
    return None


@dp.callback_query(F.data.startswith("cat_"))
async def process_category_selection(callback: CallbackQuery):
    category_index = int(callback.data.split("_")[1])
    
    
async def get_categories_with_tokens():
    with Session() as session:
        result = session.execute(select(Category).where(Category.bot_token.isnot(None)))
        categories = result.scalars().all()
    return categories    



async def main():
    dp.include_router(router)
    Base.metadata.create_all(engine)
    asyncio.create_task(receive_messages())
    categories = await get_categories_with_tokens()


    setup_message_retention(engine)
    print("prikol")
    await dp.start_polling(bot)
    for category in categories:
        await start_new_bot(category)

    try:
        while True:
            await asyncio.sleep(3600)  # Check every hour or adjust as needed
    except asyncio.CancelledError:
        # On shutdown, stop all bots
        for task in running_bots.values():
            task.cancel()
        await asyncio.gather(*running_bots.values(), return_exceptions=True)
    
    
   
    
if __name__ == "__main__":
    asyncio.run(main())






