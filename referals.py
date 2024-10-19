from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.orm import Session as SessionType
from sqlalchemy import func
from datetime import datetime
import random
import string
from message_scraper import engine
from message_scraper import User, ReferralData, ActiveSubscription

router_referrals = Router()
Session = sessionmaker(bind=engine)

def generate_referral_code(session: SessionType, chat_id: int) -> str:
    initial_code = f"ref{chat_id}"
    if not session.query(User).filter_by(referral_code=initial_code).first():
        return initial_code
    
    while True:
        code = f"ref{chat_id}" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        if not session.query(User).filter_by(referral_code=code).first():
            return code


async def cmd_referral_stats(message: Message):
    user_id = message.from_user.id
    session = Session()
    try:
        user = session.query(User).filter_by(chat_id=user_id).first()
        if not user or not user.referral_data:
            await message.answer("No referral data available.")
            return
        
        bot_username = (await message.bot.me()).username
        referral_link = f"https://t.me/{bot_username}?start={user.referral_code}"

        data = user.referral_data
        stats = f"Статистика рефералов:\n"
        stats += f"Реферальная ссылка: {referral_link}\n"
        stats += f"Реферальный баланс: {data.referral_balance:.2f}\n"
        stats += f"Оплачено рефералов: {data.referrals_paid_count}\n"
        stats += f"Доход наличными: {data.cash_income:.2f}\n"
        stats += f"Активации: {data.activations_count}\n"
        stats += f"Оплачено людей: {data.people_paid_count}\n"
        stats += f"Количество платежей: {data.payments_count}\n"
        stats += f"Сумма платежей: {data.payments_sum:.2f}\n"
        
        await message.answer(stats)
    finally:
        session.close()

@router_referrals.message(Command("my_referral_link"))
async def cmd_my_referral_link(message: Message):
    user_id = message.from_user.id
    session = Session()
    try:
        user = session.query(User).filter_by(chat_id=user_id).first()
        if not user or not user.referral_code:
            await message.answer("Ваша реферальная ссылка недоступна. Пожалуйста свяжитесь с поддержкой.")
            return
        
        bot_username = (await message.bot.me()).username
        referral_link = f"https://t.me/{bot_username}?start={user.referral_code}"
        # await message.answer(f"Your referral link is:\n{referral_link}\n\nShare this link with your friends to earn referral bonuses!")
        return referral_link
    finally:
        session.close()