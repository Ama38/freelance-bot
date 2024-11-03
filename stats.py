from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from admin import admin_only
from models import User, ActiveSubscription, SuspendedSubscription, Category, MessageRecord
from models import Session
import datetime
import logging



router_stats = Router()



class StatsStates(StatesGroup):
    choosing_table = State()
    viewing_stats = State()
    entering_id = State()
    
    
    
    
    
    
    
def get_stats_tables_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пользователи", callback_data="stats_users")],
        [InlineKeyboardButton(text="Категории", callback_data="stats_categories")],
        [InlineKeyboardButton(text="Сообщения", callback_data="stats_messages")],
        [InlineKeyboardButton(text="Активные подписки", callback_data="stats_active_subs")],
        [InlineKeyboardButton(text="Приостановленные подписки", callback_data="stats_suspended_subs")]
    ])

def get_viewing_options_keyboard(table_name: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Последние 5 записей", callback_data=f"view_last_{table_name}")],
        [InlineKeyboardButton(text="Поиск по ID", callback_data=f"view_id_{table_name}")],
        [InlineKeyboardButton(text="Назад к таблицам", callback_data="back_to_tables")]
    ])

async def format_stats_message(records, table_name: str) -> str:
    if not records:
        return "Записи не найдены"
    
    message = f"📊 Статистика {table_name}:\n\n"
    
    for record in records:
        if table_name == "users":
            # Get active subscriptions count
            active_subs_count = len([sub for sub in record.active_subscriptions if sub.end_date > datetime.utcnow()])
            
            # Get suspended subscriptions count
            suspended_subs_count = len(record.suspended_subscriptions)
            
            # Format categories
            categories = ", ".join([cat.name for cat in record.categories]) if record.categories else "Нет категорий"
            
            message += (
                f"🆔 ID: {record.id}\n"
                f"👤 Username: @{record.username}\n"
                f"📋 Имя: {record.first_name or 'Не указано'} {record.last_name or ''}\n"
                f"💬 Chat ID: {record.chat_id}\n"
                f"📊 Активные подписки: {active_subs_count}\n"
                f"⏸ Приостановленные подписки: {suspended_subs_count}\n"
                f"📁 Категории: {categories}\n"
                f"📅 Последняя активность: {max([sub.end_date for sub in record.active_subscriptions] or [datetime.min]).strftime('%d.%m.%Y %H:%M') if record.active_subscriptions else 'Нет активности'}\n"
                f"━━━━━━━━━━━━━━━\n\n"
            )
        
        elif table_name == "categories":
            users_count = len(record.users)
            active_subs_count = len([sub for sub in record.active_subscriptions if sub.end_date > datetime.utcnow()])
            
            message += (
                f"🆔 ID: {record.id}\n"
                f"📋 Название: {record.name}\n"
                f"🔑 Ключевые слова: {record.keywords}\n"
                f"💰 Цены:\n"
                f"  └ Месяц: ${record.price_monthly}\n"
                f"  └ Квартал: ${record.price_quarterly}\n"
                f"  └ Год: ${record.price_yearly}\n"
                f"👥 Пользователей: {users_count}\n"
                f"✅ Активных подписок: {active_subs_count}\n"
                f"━━━━━━━━━━━━━━━\n\n"
            )
        
        elif table_name == "messages":
            message += (
                f"🆔 ID: {record.id}\n"
                f"👤 От: {record.sender_name} (@{record.sender_username or 'Нет username'})\n"
                f"💬 Чат: {record.chat_title} (ID: {record.chat_id})\n"
                f"📁 Категория: {record.category.name}\n"
                f"🔑 Найдено по: {record.matched_keyword}\n"
                f"📅 Дата: {record.date.strftime('%d.%m.%Y %H:%M')}\n"
                f"📝 Текст: {record.text[:200]}{'...' if len(record.text) > 200 else ''}\n"
                f"━━━━━━━━━━━━━━━\n\n"
            )
        
        elif table_name == "active_subs":
            days_left = (record.end_date - datetime.utcnow()).days
            message += (
                f"🆔 ID: {record.id}\n"
                f"👤 Пользователь: {record.user.username or record.user.first_name}\n"
                f"📁 Категория: {record.category.name}\n"
                f"📅 Начало: {record.start_date.strftime('%d.%m.%Y')}\n"
                f"📅 Окончание: {record.end_date.strftime('%d.%m.%Y')}\n"
                f"⏳ Осталось дней: {days_left}\n"
                f"📋 Тип подписки: {record.subscription_type}\n"
                f"━━━━━━━━━━━━━━━\n\n"
            )
        
        elif table_name == "suspended_subs":
            message += (
                f"🆔 ID: {record.id}\n"
                f"👤 Пользователь: {record.user.username or record.user.first_name}\n"
                f"📁 Категория: {record.category.name}\n"
                f"⏸ Приостановлено: {record.suspension_date.strftime('%d.%m.%Y')}\n"
                f"📅 Изначальная дата окончания: {record.original_end_date.strftime('%d.%m.%Y')}\n"
                f"📋 Тип подписки: {record.subscription_type}\n"
                f"━━━━━━━━━━━━━━━\n\n"
            )
    
    return message

@router_stats.callback_query(lambda c: c.data.startswith("view_last_"))
async def show_last_five(callback: CallbackQuery, state: FSMContext):
    table_name = callback.data.split("_")[2]
    session = Session()
    try:
        records = []
        if table_name == "users":
            records = (session.query(User)
                      .options(joinedload(User.active_subscriptions),
                              joinedload(User.suspended_subscriptions),
                              joinedload(User.categories))
                      .order_by(desc(User.id))
                      .limit(5)
                      .all())
        elif table_name == "categories":
            records = (session.query(Category)
                      .options(joinedload(Category.users),
                              joinedload(Category.active_subscriptions))
                      .order_by(desc(Category.id))
                      .limit(5)
                      .all())
        elif table_name == "messages":
            records = (session.query(MessageRecord)
                      .options(joinedload(MessageRecord.category))
                      .order_by(desc(MessageRecord.id))
                      .limit(5)
                      .all())
        elif table_name == "active_subs":
            records = (session.query(ActiveSubscription)
                      .options(joinedload(ActiveSubscription.user),
                              joinedload(ActiveSubscription.category))
                      .order_by(desc(ActiveSubscription.id))
                      .limit(5)
                      .all())
        elif table_name == "suspended_subs":
            records = (session.query(SuspendedSubscription)
                      .options(joinedload(SuspendedSubscription.user),
                              joinedload(SuspendedSubscription.category))
                      .order_by(desc(SuspendedSubscription.id))
                      .limit(5)
                      .all())
        
        stats_message = await format_stats_message(records, table_name)
        await callback.message.edit_text(
            stats_message,
            reply_markup=get_stats_tables_keyboard()
        )
    except Exception as e:
        logging.error(f"Error in show_last_five: {e}")
        await callback.message.edit_text(
            f"Произошла ошибка при получении данных: {str(e)}",
            reply_markup=get_stats_tables_keyboard()
        )
    finally:
        session.close()

@router_stats.message(StatsStates.entering_id)
async def show_record_by_id(message: Message, state: FSMContext):
    try:
        record_id = int(message.text)
        data = await state.get_data()
        table_name = data['viewing_table']
        
        session = Session()
        try:
            record = None
            if table_name == "users":
                record = (session.query(User)
                         .options(joinedload(User.active_subscriptions),
                                 joinedload(User.suspended_subscriptions),
                                 joinedload(User.categories))
                         .filter(User.id == record_id)
                         .first())
            elif table_name == "categories":
                record = (session.query(Category)
                         .options(joinedload(Category.users),
                                 joinedload(Category.active_subscriptions))
                         .filter(Category.id == record_id)
                         .first())
            elif table_name == "messages":
                record = (session.query(MessageRecord)
                         .options(joinedload(MessageRecord.category))
                         .filter(MessageRecord.id == record_id)
                         .first())
            elif table_name == "active_subs":
                record = (session.query(ActiveSubscription)
                         .options(joinedload(ActiveSubscription.user),
                                 joinedload(ActiveSubscription.category))
                         .filter(ActiveSubscription.id == record_id)
                         .first())
            elif table_name == "suspended_subs":
                record = (session.query(SuspendedSubscription)
                         .options(joinedload(SuspendedSubscription.user),
                                 joinedload(SuspendedSubscription.category))
                         .filter(SuspendedSubscription.id == record_id)
                         .first())
            
            if record:
                stats_message = await format_stats_message([record], table_name)
                await message.answer(
                    stats_message,
                    reply_markup=get_stats_tables_keyboard()
                )
            else:
                await message.answer(
                    f"Запись с ID {record_id} не найдена",
                    reply_markup=get_stats_tables_keyboard()
                )
        finally:
            session.close()
            
    except ValueError:
        await message.answer(
            "Пожалуйста, введите корректный числовой ID",
            reply_markup=get_stats_tables_keyboard()
        )
    except Exception as e:
        logging.error(f"Error in show_record_by_id: {e}")
        await message.answer(
            f"Произошла ошибка при получении данных: {str(e)}",
            reply_markup=get_stats_tables_keyboard()
        )
        

@router_stats.message(Command('get_stats'))
@admin_only
async def handle_statistics(message: Message, state: FSMContext):

    
    await state.set_state(StatsStates.choosing_table)
    await message.answer("Выберите таблицу что бы увидеть статистику:", 
                        reply_markup=get_stats_tables_keyboard())

@router_stats.callback_query(lambda c: c.data.startswith("stats_"))
async def process_table_selection(callback: CallbackQuery, state: FSMContext):
    table_name = callback.data.split("_")[1]
    await state.update_data(selected_table=table_name)
    await callback.message.edit_text(
        f"Как бы вы хотели просмотреть статистику таблицы {table_name}?",
        reply_markup=get_viewing_options_keyboard(table_name)
    )

@router_stats.callback_query(lambda c: c.data.startswith("view_last_"))
async def show_last_five(callback: CallbackQuery, state: FSMContext):
    table_name = callback.data.split("_")[2]
    session = Session()
    try:
        if table_name == "users":
            records = session.query(User).order_by(desc(User.id)).limit(5).all()
        elif table_name == "categories":
            records = session.query(Category).order_by(desc(Category.id)).limit(5).all()
        elif table_name == "messages":
            records = session.query(MessageRecord).order_by(desc(MessageRecord.id)).limit(5).all()
        elif table_name == "active_subs":
            records = session.query(ActiveSubscription).order_by(desc(ActiveSubscription.id)).limit(5).all()
        elif table_name == "suspended_subs":
            records = session.query(SuspendedSubscription).order_by(desc(SuspendedSubscription.id)).limit(5).all()
        
        stats_message = await format_stats_message(records, table_name)
        await callback.message.edit_text(
            stats_message,
            reply_markup=get_stats_tables_keyboard()
        )
    finally:
        session.close()

@router_stats.callback_query(lambda c: c.data.startswith("view_id_"))
async def prompt_for_id(callback: CallbackQuery, state: FSMContext):
    table_name = callback.data.split("_")[2]
    await state.update_data(viewing_table=table_name)
    await state.set_state(StatsStates.entering_id)
    await callback.message.edit_text(
        f"Пожалуйста, введите идентификатор таблицы {table_name} которую вы хотите посмотреть.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Back", callback_data="back_to_tables")]
        ])
    )

@router_stats.message(StatsStates.entering_id)
async def show_record_by_id(message: Message, state: FSMContext):
    try:
        record_id = int(message.text)
        data = await state.get_data()
        table_name = data['viewing_table']
        
        session = Session()
        try:
            if table_name == "users":
                record = session.query(User).filter(User.id == record_id).first()
            elif table_name == "categories":
                record = session.query(Category).filter(Category.id == record_id).first()
            elif table_name == "messages":
                record = session.query(MessageRecord).filter(MessageRecord.id == record_id).first()
            elif table_name == "active_subs":
                record = session.query(ActiveSubscription).filter(ActiveSubscription.id == record_id).first()
            elif table_name == "suspended_subs":
                record = session.query(SuspendedSubscription).filter(SuspendedSubscription.id == record_id).first()
            
            if record:
                stats_message = await format_stats_message([record], table_name)
                await message.answer(
                    stats_message,
                    reply_markup=get_stats_tables_keyboard()
                )
            else:
                await message.answer(
                    f"No record found with ID {record_id}",
                    reply_markup=get_stats_tables_keyboard()
                )
        finally:
            session.close()
            
    except ValueError:
        await message.answer(
            "Пожалуйста, введите действительный цифровой идентификатор",
            reply_markup=get_stats_tables_keyboard()
        )

@router_stats.callback_query(lambda c: c.data == "back_to_tables")
async def back_to_tables(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StatsStates.choosing_table)
    await callback.message.edit_text(
        "Select a table to view statistics:",
        reply_markup=get_stats_tables_keyboard()
    )