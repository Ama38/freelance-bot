from message_scraper import Base, engine, User, MessageRecord, Category
from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, joinedload
from datetime import datetime, timedelta
from message_scraper import ActiveSubscription, SuspendedSubscription
Session = sessionmaker(bind=engine)
import logging

router_subscriptions = Router()

@router_subscriptions.message(F.text == "✅ Мои подписки")
async def handle_my_subscriptions(message: Message):
    user_id = message.from_user.id
    session = Session()
    try:
        user = session.query(User).options(
            joinedload(User.active_subscriptions),
            joinedload(User.suspended_subscriptions)
        ).filter(User.chat_id == user_id).first()

        if not user:
            await message.answer("Пользователь не найден. Пожалуйста, начните с команды /start.")
            return

        current_time = datetime.utcnow()
        active_subscriptions = [sub for sub in user.active_subscriptions if sub.end_date > current_time]
        suspended_subscriptions = user.suspended_subscriptions

        logging.info(f"User {user_id} has {len(active_subscriptions)} active and {len(suspended_subscriptions)} suspended subscriptions")

        builder = InlineKeyboardBuilder()
        
        if active_subscriptions:
            builder.button(text="Активные подписки", callback_data="view_active_subs")
        
        if suspended_subscriptions:
            builder.button(text="Приостановленные подписки", callback_data="view_suspended_subs")
        
        if active_subscriptions:
            builder.button(text="Приостановить подписку", callback_data="suspend_subscription")
        
        builder.button(text="Закрыть", callback_data="close_subs")
        builder.adjust(1)

        if not active_subscriptions and not suspended_subscriptions:
            await message.answer("У вас нет активных или приостановленных подписок.")
        else:
            await message.answer(
                "Управление подписками:",
                reply_markup=builder.as_markup()
            )
    except Exception as e:
        logging.error(f"Error in handle_my_subscriptions: {e}")
        await message.answer("Произошла ошибка при загрузке подписок. Пожалуйста, попробуйте позже.")
    finally:
        session.close()



@router_subscriptions.callback_query(F.data == "view_active_subs")
async def view_active_subscriptions(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    session = Session()
    try:
        user = session.query(User).options(
            joinedload(User.active_subscriptions).joinedload(ActiveSubscription.category)
        ).filter(User.chat_id == user_id).first()

        if not user:
            logging.warning(f"User with chat_id {user_id} not found in database")
            await callback_query.answer("Пользователь не найден. Пожалуйста, начните с команды /start.")
            return

        current_time = datetime.utcnow()
        active_subscriptions = [sub for sub in user.active_subscriptions if sub.end_date > current_time]

        logging.info(f"User {user_id} has {len(active_subscriptions)} active subscriptions")

        builder = InlineKeyboardBuilder()
        for sub in active_subscriptions:
            builder.button(
                text=f"{sub.category.name} (до {sub.end_date.strftime('%d.%m.%Y')})",
                callback_data=f"manage_sub_{sub.id}"
            )
        builder.button(text="Назад", callback_data="back_to_main_subs")
        builder.adjust(1)

        await callback_query.message.edit_text(
            "Ваши активные подписки:" if active_subscriptions else "У вас нет активных подписок.",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logging.error(f"Error in view_active_subscriptions: {e}")
        await callback_query.answer("Произошла ошибка при загрузке подписок. Пожалуйста, попробуйте позже.")
    finally:
        session.close()

@router_subscriptions.callback_query(F.data == "view_suspended_subs")
async def view_suspended_subscriptions(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    session = Session()
    try:
        user = session.query(User).options(
            joinedload(User.suspended_subscriptions).joinedload(SuspendedSubscription.category)
        ).filter(User.chat_id == user_id).first()

        if not user:
            logging.warning(f"User with chat_id {user_id} not found in database")
            await callback_query.answer("Пользователь не найден. Пожалуйста, начните с команды /start.")
            return

        suspended_subscriptions = user.suspended_subscriptions

        logging.info(f"User {user_id} has {len(suspended_subscriptions)} suspended subscriptions")

        builder = InlineKeyboardBuilder()
        for sub in suspended_subscriptions:
            builder.button(
                text=f"{sub.category.name} (с {sub.suspension_date.strftime('%d.%m.%Y')})",
                callback_data=f"reactivate_sub_{sub.id}"
            )
        builder.button(text="Назад", callback_data="back_to_main_subs")
        builder.adjust(1)

        await callback_query.message.edit_text(
            "Ваши приостановленные подписки:" if suspended_subscriptions else "У вас нет приостановленных подписок.",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logging.error(f"Error in view_suspended_subscriptions: {e}")
        await callback_query.answer("Произошла ошибка при загрузке подписок. Пожалуйста, попробуйте позже.")
    finally:
        session.close()

@router_subscriptions.callback_query(F.data == "suspend_subscription")
async def suspend_subscription_menu(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    session = Session()
    try:
        user = session.query(User).options(
            joinedload(User.active_subscriptions).joinedload(ActiveSubscription.category)
        ).filter(User.chat_id == user_id).first()

        if not user:
            logging.warning(f"User with chat_id {user_id} not found in database")
            await callback_query.answer("Пользователь не найден. Пожалуйста, начните с команды /start.")
            return

        current_time = datetime.utcnow()
        active_subscriptions = [sub for sub in user.active_subscriptions if sub.end_date > current_time]

        logging.info(f"User {user_id} has {len(active_subscriptions)} active subscriptions")

        builder = InlineKeyboardBuilder()
        for sub in active_subscriptions:
            builder.button(
                text=f"Приостановить {sub.category.name}",
                callback_data=f"confirm_suspend_{sub.id}"
            )
        builder.button(text="Назад", callback_data="back_to_main_subs")
        builder.adjust(1)

        await callback_query.message.edit_text(
            "Выберите подписку для приостановки:" if active_subscriptions else "У вас нет активных подписок для приостановки.",
            reply_markup=builder.as_markup()
        )
    except Exception as e:
        logging.error(f"Error in suspend_subscription_menu: {e}")
        await callback_query.answer("Произошла ошибка при загрузке подписок. Пожалуйста, попробуйте позже.")
    finally:
        session.close()

@router_subscriptions.callback_query(F.data.startswith("confirm_suspend_"))
async def confirm_suspend_subscription(callback_query: CallbackQuery):
    sub_id = int(callback_query.data.split('_')[2])
    session = Session()
    try:
        active_sub = session.query(ActiveSubscription).options(
            joinedload(ActiveSubscription.user),
            joinedload(ActiveSubscription.category)
        ).get(sub_id)

        if not active_sub:
            logging.warning(f"Active subscription with id {sub_id} not found")
            await callback_query.answer("Подписка не найдена.")
            return

        suspended_sub = SuspendedSubscription(
            user_id=active_sub.user_id,
            category_id=active_sub.category_id,
            suspension_date=datetime.utcnow(),
            original_end_date=active_sub.end_date,
            subscription_type=active_sub.subscription_type
        )
        session.add(suspended_sub)
        session.delete(active_sub)
        session.commit()

        logging.info(f"Subscription {sub_id} suspended for user {active_sub.user_id}. Active subscription deleted.")

        await callback_query.answer("Подписка успешно приостановлена.")
        # await handle_my_subscriptions(callback_query.message)
    except Exception as e:
        logging.error(f"Error in confirm_suspend_subscription: {e}")
        session.rollback()
        await callback_query.answer("Произошла ошибка при приостановке подписки. Пожалуйста, попробуйте позже.")
    finally:
        session.close()

@router_subscriptions.callback_query(F.data.startswith("reactivate_sub_"))
async def reactivate_subscription(callback_query: CallbackQuery):
    sub_id = int(callback_query.data.split('_')[2])
    session = Session()
    try:
        suspended_sub = session.query(SuspendedSubscription).options(
            joinedload(SuspendedSubscription.user),
            joinedload(SuspendedSubscription.category)
        ).get(sub_id)

        if not suspended_sub:
            logging.warning(f"Suspended subscription with id {sub_id} not found")
            await callback_query.answer("Приостановленная подписка не найдена.")
            return

        current_time = datetime.utcnow()
        suspension_duration = current_time - suspended_sub.suspension_date
        new_end_date = suspended_sub.original_end_date + suspension_duration

        active_sub = ActiveSubscription(
            user_id=suspended_sub.user_id,
            category_id=suspended_sub.category_id,
            start_date=current_time,
            end_date=new_end_date,
            subscription_type=suspended_sub.subscription_type
        )
        session.add(active_sub)
        session.delete(suspended_sub)  
        session.commit()

        logging.info(f"Subscription {sub_id} reactivated for user {suspended_sub.user_id}. Suspended subscription deleted.")

        await callback_query.answer("Подписка успешно возобновлена.")
        #await handle_my_subscriptions(callback_query.message)
    except Exception as e:
        logging.error(f"Error in reactivate_subscription: {e}")
        session.rollback()
        await callback_query.answer("Произошла ошибка при возобновлении подписки. Пожалуйста, попробуйте позже.")
    finally:
        session.close()

PERSONAL_CABINET = '''«✅ Мои подписки» -  список твоих активных подписок, приостановка или перенос подписки

«⛔️ Стоп слова ⛔️» - добавление слов по которым не будут пересылаться сообщения

«💵 Реферальная система» - условия и реф ссылка

«👥 Аккаунты» - добавление до 3-х аккаунтов в каждом направлении*

«📊 Статистика» - скольким людям написал с каждого аккаунта*

«📋 Гугл таблицы» - выгрузка статистики в гугл таблицу*

*Доступно только при годовой подписке'''


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




@router_subscriptions.callback_query(F.data == "back_to_main_subs")
async def back_to_main_subs(callback_query: CallbackQuery):
    await callback_query.message.answer(PERSONAL_CABINET, reply_markup=keyboard_personal_cabinet)

@router_subscriptions.callback_query(F.data == "close_subs")
async def close_subscriptions(callback_query: CallbackQuery):
    await callback_query.message.delete()







    








