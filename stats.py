# from aiogram import router_stats, F
# from aiogram.fsm.state import StatesGroup, State
# from aiogram.filters import Command
# from aiogram.fsm.context import FSMContext
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
# from sqlalchemy.orm import joinedload
# from sqlalchemy import desc
# from admin import admin_only
# from models import User, ActiveSubscription, SuspendedSubscription, Category, MessageRecord
# from models import Session
# import datetime
# import logging
from admin import admin_only
from models import *






# class StatsStates(StatesGroup):
#     choosing_table = State()
#     viewing_stats = State()
#     entering_id = State()
    
    
    
    
    
    
    
# def get_stats_tables_keyboard():
#     return InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="Пользователи", callback_data="stats_users")],
#         [InlineKeyboardButton(text="Категории", callback_data="stats_categories")],
#         [InlineKeyboardButton(text="Сообщения", callback_data="stats_messages")],
#         [InlineKeyboardButton(text="Активные подписки", callback_data="stats_active_subs")],
#         [InlineKeyboardButton(text="Приостановленные подписки", callback_data="stats_suspended_subs")]
#     ])

# def get_viewing_options_keyboard(table_name: str):
#     return InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="Последние 5 записей", callback_data=f"view_last_{table_name}")],
#         [InlineKeyboardButton(text="Поиск по ID", callback_data=f"view_id_{table_name}")],
#         [InlineKeyboardButton(text="Назад к таблицам", callback_data="back_to_tables")]
#     ])

# async def format_stats_message(records, table_name: str) -> str:
#     if not records:
#         return "Записи не найдены"
    
#     message = f"📊 Статистика {table_name}:\n\n"
    
#     for record in records:
#         if table_name == "users":
#             # Get active subscriptions count
#             active_subs_count = len([sub for sub in record.active_subscriptions if sub.end_date > datetime.utcnow()])
            
#             # Get suspended subscriptions count
#             suspended_subs_count = len(record.suspended_subscriptions)
            
#             # Format categories
#             categories = ", ".join([cat.name for cat in record.categories]) if record.categories else "Нет категорий"
            
#             message += (
#                 f"🆔 ID: {record.id}\n"
#                 f"👤 Username: @{record.username}\n"
#                 f"📋 Имя: {record.first_name or 'Не указано'} {record.last_name or ''}\n"
#                 f"💬 Chat ID: {record.chat_id}\n"
#                 f"📊 Активные подписки: {active_subs_count}\n"
#                 f"⏸ Приостановленные подписки: {suspended_subs_count}\n"
#                 f"📁 Категории: {categories}\n"
#                 f"📅 Последняя активность: {max([sub.end_date for sub in record.active_subscriptions] or [datetime.min]).strftime('%d.%m.%Y %H:%M') if record.active_subscriptions else 'Нет активности'}\n"
#                 f"━━━━━━━━━━━━━━━\n\n"
#             )
        
#         elif table_name == "categories":
#             users_count = len(record.users)
#             active_subs_count = len([sub for sub in record.active_subscriptions if sub.end_date > datetime.utcnow()])
            
#             message += (
#                 f"🆔 ID: {record.id}\n"
#                 f"📋 Название: {record.name}\n"
#                 f"🔑 Ключевые слова: {record.keywords}\n"
#                 f"💰 Цены:\n"
#                 f"  └ Месяц: ${record.price_monthly}\n"
#                 f"  └ Квартал: ${record.price_quarterly}\n"
#                 f"  └ Год: ${record.price_yearly}\n"
#                 f"👥 Пользователей: {users_count}\n"
#                 f"✅ Активных подписок: {active_subs_count}\n"
#                 f"━━━━━━━━━━━━━━━\n\n"
#             )
        
#         elif table_name == "messages":
#             message += (
#                 f"🆔 ID: {record.id}\n"
#                 f"👤 От: {record.sender_name} (@{record.sender_username or 'Нет username'})\n"
#                 f"💬 Чат: {record.chat_title} (ID: {record.chat_id})\n"
#                 f"📁 Категория: {record.category.name}\n"
#                 f"🔑 Найдено по: {record.matched_keyword}\n"
#                 f"📅 Дата: {record.date.strftime('%d.%m.%Y %H:%M')}\n"
#                 f"📝 Текст: {record.text[:200]}{'...' if len(record.text) > 200 else ''}\n"
#                 f"━━━━━━━━━━━━━━━\n\n"
#             )
        
#         elif table_name == "active_subs":
#             days_left = (record.end_date - datetime.utcnow()).days
#             message += (
#                 f"🆔 ID: {record.id}\n"
#                 f"👤 Пользователь: {record.user.username or record.user.first_name}\n"
#                 f"📁 Категория: {record.category.name}\n"
#                 f"📅 Начало: {record.start_date.strftime('%d.%m.%Y')}\n"
#                 f"📅 Окончание: {record.end_date.strftime('%d.%m.%Y')}\n"
#                 f"⏳ Осталось дней: {days_left}\n"
#                 f"📋 Тип подписки: {record.subscription_type}\n"
#                 f"━━━━━━━━━━━━━━━\n\n"
#             )
        
#         elif table_name == "suspended_subs":
#             message += (
#                 f"🆔 ID: {record.id}\n"
#                 f"👤 Пользователь: {record.user.username or record.user.first_name}\n"
#                 f"📁 Категория: {record.category.name}\n"
#                 f"⏸ Приостановлено: {record.suspension_date.strftime('%d.%m.%Y')}\n"
#                 f"📅 Изначальная дата окончания: {record.original_end_date.strftime('%d.%m.%Y')}\n"
#                 f"📋 Тип подписки: {record.subscription_type}\n"
#                 f"━━━━━━━━━━━━━━━\n\n"
#             )
    
#     return message

# @router_stats.callback_query(lambda c: c.data.startswith("view_last_"))
# async def show_last_five(callback: CallbackQuery, state: FSMContext):
#     table_name = callback.data.split("_")[2]
#     session = Session()
#     try:
#         records = []
#         if table_name == "users":
#             records = (session.query(User)
#                       .options(joinedload(User.active_subscriptions),
#                               joinedload(User.suspended_subscriptions),
#                               joinedload(User.categories))
#                       .order_by(desc(User.id))
#                       .limit(5)
#                       .all())
#         elif table_name == "categories":
#             records = (session.query(Category)
#                       .options(joinedload(Category.users),
#                               joinedload(Category.active_subscriptions))
#                       .order_by(desc(Category.id))
#                       .limit(5)
#                       .all())
#         elif table_name == "messages":
#             records = (session.query(MessageRecord)
#                       .options(joinedload(MessageRecord.category))
#                       .order_by(desc(MessageRecord.id))
#                       .limit(5)
#                       .all())
#         elif table_name == "active_subs":
#             records = (session.query(ActiveSubscription)
#                       .options(joinedload(ActiveSubscription.user),
#                               joinedload(ActiveSubscription.category))
#                       .order_by(desc(ActiveSubscription.id))
#                       .limit(5)
#                       .all())
#         elif table_name == "suspended_subs":
#             records = (session.query(SuspendedSubscription)
#                       .options(joinedload(SuspendedSubscription.user),
#                               joinedload(SuspendedSubscription.category))
#                       .order_by(desc(SuspendedSubscription.id))
#                       .limit(5)
#                       .all())
        
#         stats_message = await format_stats_message(records, table_name)
#         await callback.message.edit_text(
#             stats_message,
#             reply_markup=get_stats_tables_keyboard()
#         )
#     except Exception as e:
#         logging.error(f"Error in show_last_five: {e}")
#         await callback.message.edit_text(
#             f"Произошла ошибка при получении данных: {str(e)}",
#             reply_markup=get_stats_tables_keyboard()
#         )
#     finally:
#         session.close()

# @router_stats.message(StatsStates.entering_id)
# async def show_record_by_id(message: Message, state: FSMContext):
#     try:
#         record_id = int(message.text)
#         data = await state.get_data()
#         table_name = data['viewing_table']
        
#         session = Session()
#         try:
#             record = None
#             if table_name == "users":
#                 record = (session.query(User)
#                          .options(joinedload(User.active_subscriptions),
#                                  joinedload(User.suspended_subscriptions),
#                                  joinedload(User.categories))
#                          .filter(User.id == record_id)
#                          .first())
#             elif table_name == "categories":
#                 record = (session.query(Category)
#                          .options(joinedload(Category.users),
#                                  joinedload(Category.active_subscriptions))
#                          .filter(Category.id == record_id)
#                          .first())
#             elif table_name == "messages":
#                 record = (session.query(MessageRecord)
#                          .options(joinedload(MessageRecord.category))
#                          .filter(MessageRecord.id == record_id)
#                          .first())
#             elif table_name == "active_subs":
#                 record = (session.query(ActiveSubscription)
#                          .options(joinedload(ActiveSubscription.user),
#                                  joinedload(ActiveSubscription.category))
#                          .filter(ActiveSubscription.id == record_id)
#                          .first())
#             elif table_name == "suspended_subs":
#                 record = (session.query(SuspendedSubscription)
#                          .options(joinedload(SuspendedSubscription.user),
#                                  joinedload(SuspendedSubscription.category))
#                          .filter(SuspendedSubscription.id == record_id)
#                          .first())
            
#             if record:
#                 stats_message = await format_stats_message([record], table_name)
#                 await message.answer(
#                     stats_message,
#                     reply_markup=get_stats_tables_keyboard()
#                 )
#             else:
#                 await message.answer(
#                     f"Запись с ID {record_id} не найдена",
#                     reply_markup=get_stats_tables_keyboard()
#                 )
#         finally:
#             session.close()
            
#     except ValueError:
#         await message.answer(
#             "Пожалуйста, введите корректный числовой ID",
#             reply_markup=get_stats_tables_keyboard()
#         )
#     except Exception as e:
#         logging.error(f"Error in show_record_by_id: {e}")
#         await message.answer(
#             f"Произошла ошибка при получении данных: {str(e)}",
#             reply_markup=get_stats_tables_keyboard()
#         )
        

# @router_stats.message(Command('get_stats'))
# @admin_only
# async def handle_statistics(message: Message, state: FSMContext):

    
#     await state.set_state(StatsStates.choosing_table)
#     await message.answer("Выберите таблицу что бы увидеть статистику:", 
#                         reply_markup=get_stats_tables_keyboard())

# @router_stats.callback_query(lambda c: c.data.startswith("stats_"))
# async def process_table_selection(callback: CallbackQuery, state: FSMContext):
#     table_name = callback.data.split("_")[1]
#     await state.update_data(selected_table=table_name)
#     await callback.message.edit_text(
#         f"Как бы вы хотели просмотреть статистику таблицы {table_name}?",
#         reply_markup=get_viewing_options_keyboard(table_name)
#     )

# @router_stats.callback_query(lambda c: c.data.startswith("view_last_"))
# async def show_last_five(callback: CallbackQuery, state: FSMContext):
#     table_name = callback.data.split("_")[2]
#     session = Session()
#     try:
#         if table_name == "users":
#             records = session.query(User).order_by(desc(User.id)).limit(5).all()
#         elif table_name == "categories":
#             records = session.query(Category).order_by(desc(Category.id)).limit(5).all()
#         elif table_name == "messages":
#             records = session.query(MessageRecord).order_by(desc(MessageRecord.id)).limit(5).all()
#         elif table_name == "active_subs":
#             records = session.query(ActiveSubscription).order_by(desc(ActiveSubscription.id)).limit(5).all()
#         elif table_name == "suspended_subs":
#             records = session.query(SuspendedSubscription).order_by(desc(SuspendedSubscription.id)).limit(5).all()
        
#         stats_message = await format_stats_message(records, table_name)
#         await callback.message.edit_text(
#             stats_message,
#             reply_markup=get_stats_tables_keyboard()
#         )
#     finally:
#         session.close()

# @router_stats.callback_query(lambda c: c.data.startswith("view_id_"))
# async def prompt_for_id(callback: CallbackQuery, state: FSMContext):
#     table_name = callback.data.split("_")[2]
#     await state.update_data(viewing_table=table_name)
#     await state.set_state(StatsStates.entering_id)
#     await callback.message.edit_text(
#         f"Пожалуйста, введите идентификатор таблицы {table_name} которую вы хотите посмотреть.",
#         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
#             [InlineKeyboardButton(text="Back", callback_data="back_to_tables")]
#         ])
#     )

# @router_stats.message(StatsStates.entering_id)
# async def show_record_by_id(message: Message, state: FSMContext):
#     try:
#         record_id = int(message.text)
#         data = await state.get_data()
#         table_name = data['viewing_table']
        
#         session = Session()
#         try:
#             if table_name == "users":
#                 record = session.query(User).filter(User.id == record_id).first()
#             elif table_name == "categories":
#                 record = session.query(Category).filter(Category.id == record_id).first()
#             elif table_name == "messages":
#                 record = session.query(MessageRecord).filter(MessageRecord.id == record_id).first()
#             elif table_name == "active_subs":
#                 record = session.query(ActiveSubscription).filter(ActiveSubscription.id == record_id).first()
#             elif table_name == "suspended_subs":
#                 record = session.query(SuspendedSubscription).filter(SuspendedSubscription.id == record_id).first()
            
#             if record:
#                 stats_message = await format_stats_message([record], table_name)
#                 await message.answer(
#                     stats_message,
#                     reply_markup=get_stats_tables_keyboard()
#                 )
#             else:
#                 await message.answer(
#                     f"No record found with ID {record_id}",
#                     reply_markup=get_stats_tables_keyboard()
#                 )
#         finally:
#             session.close()
            
#     except ValueError:
#         await message.answer(
#             "Пожалуйста, введите действительный цифровой идентификатор",
#             reply_markup=get_stats_tables_keyboard()
#         )

# @router_stats.callback_query(lambda c: c.data == "back_to_tables")
# async def back_to_tables(callback: CallbackQuery, state: FSMContext):
#     await state.set_state(StatsStates.choosing_table)
#     await callback.message.edit_text(
#         "Select a table to view statistics:",
#         reply_markup=get_stats_tables_keyboard()
#     )




from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import func
from datetime import datetime
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart import BarChart, Reference
import os
from io import BytesIO

# Import your models and Session
from models import Session, User, Admin, Category, ActiveSubscription, SuspendedSubscription, ReferralData

router_stats = Router()

def get_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Users Report 👥", callback_data="report_users"),
            InlineKeyboardButton(text="Categories Report 📑", callback_data="report_categories")
        ],
        [
            InlineKeyboardButton(text="Financial Report 💰", callback_data="report_financial"),
            InlineKeyboardButton(text="Subscriptions Report 📊", callback_data="report_subs")
        ],
        [
            InlineKeyboardButton(text="Full Report 📈", callback_data="report_full"),
            InlineKeyboardButton(text="Referrals Report 👥", callback_data="report_referrals")
        ]
    ])

@router_stats.message(Command("admin"))
async def admin_command(message: Message):
    try:
        with Session() as session:
            admin = session.query(Admin).filter(Admin.telegram_id == message.from_user.id).first()
            if not admin:
                await message.answer("You don't have access to admin panel.")
                return
            
            await message.answer("📊 Admin Panel - Choose report type:", reply_markup=get_admin_keyboard())
    except Exception as e:
        await message.answer(f"Error accessing admin panel: {str(e)}")

@router_stats.callback_query(F.data.startswith("report_"))
async def handle_report_callbacks(callback: CallbackQuery):
    await callback.answer()
    report_type = callback.data.split("_")[1]
    
    try:
        # Create temporary file path
        temp_file_path = f"temp_{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        await callback.message.answer("Generating report, please wait...")
        
        if report_type == "users":
            await generate_users_report(temp_file_path)
            caption = "Users Report"
        elif report_type == "categories":
            await generate_categories_report(temp_file_path)
            caption = "Categories Report"
        elif report_type == "financial":
            await generate_financial_report(temp_file_path)
            caption = "Financial Report"
        elif report_type == "subs":
            await generate_subscriptions_report(temp_file_path)
            caption = "Subscriptions Report"
        elif report_type == "referrals":
            await generate_referrals_report(temp_file_path)
            caption = "Referrals Report"
        else:  # full report
            await generate_full_report(temp_file_path)
            caption = "Full Report"

        # Send document using FSInputFile
        await callback.message.answer_document(
            document=FSInputFile(temp_file_path),
            caption=f"📊 {caption} - {datetime.now().strftime('%Y-%m-%d')}"
        )
        
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
    except Exception as e:
        await callback.message.answer(f"Error generating report: {str(e)}")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

async def generate_users_report(file_path: str):
    wb = Workbook()
    ws = wb.active
    ws.title = "Users Analysis"
    
    with Session() as session:
        users = session.query(User).all()
        
        users_data = []
        for user in users:
            active_subs = session.query(func.count(ActiveSubscription.id))\
                .filter(ActiveSubscription.user_id == user.id).scalar()
            referred_users = session.query(func.count(User.id))\
                .filter(User.referred_by_id == user.id).scalar()
                
            users_data.append({
                'User ID': user.id,
                'Username': user.username,
                'Full Name': f"{user.first_name or ''} {user.last_name or ''}".strip(),
                'Active Subscriptions': active_subs,
                'Referred Users': referred_users,
                'Total Categories': len(user.categories)
            })
    
    df = pd.DataFrame(users_data)
    
    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
        ws.append(row)
        if r_idx == 1:
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    
    wb.save(file_path)

async def generate_categories_report(file_path: str):
    wb = Workbook()
    ws = wb.active
    ws.title = "Categories Analysis"
    
    with Session() as session:
        categories = session.query(Category).all()
        
        categories_data = []
        for category in categories:
            active_subs = session.query(func.count(ActiveSubscription.id))\
                .filter(ActiveSubscription.category_id == category.id).scalar()
            suspended_subs = session.query(func.count(SuspendedSubscription.id))\
                .filter(SuspendedSubscription.category_id == category.id).scalar()
                
            categories_data.append({
                'Category': category.name,
                'Monthly Price': category.price_monthly,
                'Quarterly Price': category.price_quarterly,
                'Yearly Price': category.price_yearly,
                'Active Users': len(category.users),
                'Active Subscriptions': active_subs,
                'Suspended Subscriptions': suspended_subs,
                'Keywords': category.keywords
            })
    
    df = pd.DataFrame(categories_data)
    
    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
        ws.append(row)
        if r_idx == 1:
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    
    wb.save(file_path)

async def generate_financial_report(file_path: str):
    wb = Workbook()
    ws = wb.active
    ws.title = "Financial Analysis"
    
    with Session() as session:
        categories = session.query(Category).all()
        
        financial_data = []
        total_revenue = 0
        
        for category in categories:
            monthly_subs = session.query(func.count(ActiveSubscription.id))\
                .filter(ActiveSubscription.category_id == category.id)\
                .filter(ActiveSubscription.subscription_type == 'monthly').scalar()
            quarterly_subs = session.query(func.count(ActiveSubscription.id))\
                .filter(ActiveSubscription.category_id == category.id)\
                .filter(ActiveSubscription.subscription_type == 'quarterly').scalar()
            yearly_subs = session.query(func.count(ActiveSubscription.id))\
                .filter(ActiveSubscription.category_id == category.id)\
                .filter(ActiveSubscription.subscription_type == 'yearly').scalar()
                
            monthly_revenue = monthly_subs * category.price_monthly
            quarterly_revenue = quarterly_subs * category.price_quarterly
            yearly_revenue = yearly_subs * category.price_yearly
            category_total = monthly_revenue + quarterly_revenue + yearly_revenue
            total_revenue += category_total
            
            financial_data.append({
                'Category': category.name,
                'Monthly Subscribers': monthly_subs,
                'Monthly Revenue': monthly_revenue,
                'Quarterly Subscribers': quarterly_subs,
                'Quarterly Revenue': quarterly_revenue,
                'Yearly Subscribers': yearly_subs,
                'Yearly Revenue': yearly_revenue,
                'Total Revenue': category_total
            })
    
    df = pd.DataFrame(financial_data)
    df.loc[len(df)] = ['TOTAL', 
                       df['Monthly Subscribers'].sum(),
                       df['Monthly Revenue'].sum(),
                       df['Quarterly Subscribers'].sum(),
                       df['Quarterly Revenue'].sum(),
                       df['Yearly Subscribers'].sum(),
                       df['Yearly Revenue'].sum(),
                       total_revenue]
    
    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
        ws.append(row)
        if r_idx == 1:
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    
    wb.save(file_path)

async def generate_subscriptions_report(file_path: str):
    wb = Workbook()
    ws = wb.active
    ws.title = "Subscriptions Analysis"
    
    with Session() as session:
        active_subs = session.query(ActiveSubscription).all()
        
        subs_data = []
        for sub in active_subs:
            subs_data.append({
                'User': f"{sub.user.username or ''} ({sub.user.id})",
                'Category': sub.category.name,
                'Type': sub.subscription_type,
                'Start Date': sub.start_date.strftime('%Y-%m-%d'),
                'End Date': sub.end_date.strftime('%Y-%m-%d'),
                'Days Left': (sub.end_date - datetime.now()).days,
                'Price': getattr(sub.category, f'price_{sub.subscription_type}')
            })
    
    df = pd.DataFrame(subs_data)
    
    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
        ws.append(row)
        if r_idx == 1:
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    
    wb.save(file_path)

async def generate_referrals_report(file_path: str):
    wb = Workbook()
    ws = wb.active
    ws.title = "Referrals Analysis"
    
    with Session() as session:
        referral_data = session.query(ReferralData).all()
        
        ref_data = []
        for ref in referral_data:
            if ref.referrals_paid_count > 0:  # Only include users with referrals
                ref_data.append({
                    'User': f"{ref.user.username or ''} ({ref.user.id})",
                    'Balance': ref.referral_balance,
                    'Paid Referrals': ref.referrals_paid_count,
                    'Cash Income': ref.cash_income,
                    'Activations': ref.activations_count,
                    'Total Payments': ref.payments_sum,
                    'Average Payment': ref.payments_sum / ref.payments_count if ref.payments_count else 0
                })
    
    df = pd.DataFrame(ref_data)
    
    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
        ws.append(row)
        if r_idx == 1:
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    
    wb.save(file_path)

async def generate_full_report(file_path: str):
    wb = Workbook()
    
    # Users Analysis
    ws = wb.active
    ws.title = "Users"
    with Session() as session:
        users = session.query(User).all()
        users_data = []
        for user in users:
            active_subs = session.query(func.count(ActiveSubscription.id))\
                .filter(ActiveSubscription.user_id == user.id).scalar()
            referred_users = session.query(func.count(User.id))\
                .filter(User.referred_by_id == user.id).scalar()
            users_data.append({
                'User ID': user.id,
                'Username': user.username,
                'Full Name': f"{user.first_name or ''} {user.last_name or ''}".strip(),
                'Active Subscriptions': active_subs,
                'Referred Users': referred_users,
                'Total Categories': len(user.categories)
            })
    
    df_users = pd.DataFrame(users_data)
    for r_idx, row in enumerate(dataframe_to_rows(df_users, index=False, header=True), 1):
        ws.append(row)
        if r_idx == 1:
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    
    # Categories Analysis
    ws = wb.create_sheet("Categories")
    with Session() as session:
        categories = session.query(Category).all()
        categories_data = []
        for category in categories:
            active_subs = session.query(func.count(ActiveSubscription.id))\
                .filter(ActiveSubscription.category_id == category.id).scalar()
            categories_data.append({
                'Category': category.name,
                'Monthly Price': category.price_monthly,
                'Quarterly Price': category.price_quarterly,
                'Yearly Price': category.price_yearly,
                'Active Users': len(category.users),
                'Active Subscriptions': active_subs
            })
    
    df_categories = pd.DataFrame(categories_data)
    for r_idx, row in enumerate(dataframe_to_rows(df_categories, index=False, header=True), 1):
        ws.append(row)
        if r_idx == 1:
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    
    # Financial Analysis
    ws = wb.create_sheet("Financial")
    with Session() as session:
        financial_data = []
        for category in categories:
            monthly_subs = session.query(func.count(ActiveSubscription.id))\
                .filter(ActiveSubscription.category_id == category.id)\
                .filter(ActiveSubscription.subscription_type == 'monthly').scalar()
            quarterly_subs = session.query(func.count(ActiveSubscription.id))\
                .filter(ActiveSubscription.category_id == category.id)\
                .filter(ActiveSubscription.subscription_type == 'quarterly').scalar()
            yearly_subs = session.query(func.count(ActiveSubscription.id))\
                .filter(ActiveSubscription.category_id == category.id)\
                .filter(ActiveSubscription.subscription_type == 'yearly').scalar()
            
            monthly_revenue = monthly_subs * category.price_monthly
            quarterly_revenue = quarterly_subs * category.price_quarterly
            yearly_revenue = yearly_subs * category.price_yearly
            
            financial_data.append({
                'Category': category.name,
                'Monthly Revenue': monthly_revenue,
                'Quarterly Revenue': quarterly_revenue,
                'Yearly Revenue': yearly_revenue,
                'Total Revenue': monthly_revenue + quarterly_revenue + yearly_revenue
            })
    
    df_financial = pd.DataFrame(financial_data)
    df_financial.loc[len(df_financial)] = ['TOTAL', 
                                         df_financial['Monthly Revenue'].sum(),
                                         df_financial['Quarterly Revenue'].sum(),
                                         df_financial['Yearly Revenue'].sum(),
                                         df_financial['Total Revenue'].sum()]
    
    for r_idx, row in enumerate(dataframe_to_rows(df_financial, index=False, header=True), 1):
        ws.append(row)
        if r_idx == 1:
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    
    # Subscriptions Analysis
    ws = wb.create_sheet("Subscriptions")
    with Session() as session:
        active_subs = session.query(ActiveSubscription).all()
        subs_data = []
        for sub in active_subs:
            subs_data.append({
                'User': f"{sub.user.username or ''} ({sub.user.id})",
                'Category': sub.category.name,
                'Type': sub.subscription_type,
                'Start Date': sub.start_date.strftime('%Y-%m-%d'),
                'End Date': sub.end_date.strftime('%Y-%m-%d'),
                'Days Left': (sub.end_date - datetime.now()).days,
                'Price': getattr(sub.category, f'price_{sub.subscription_type}')
            })
    
    df_subs = pd.DataFrame(subs_data)
    for r_idx, row in enumerate(dataframe_to_rows(df_subs, index=False, header=True), 1):
        ws.append(row)
        if r_idx == 1:
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")

    # Referrals Analysis
    ws = wb.create_sheet("Referrals")
    with Session() as session:
        referral_data = session.query(ReferralData).all()
        ref_data = []
        for ref in referral_data:
            if ref.referrals_paid_count > 0:
                ref_data.append({
                    'User': f"{ref.user.username or ''} ({ref.user.id})",
                    'Balance': ref.referral_balance,
                    'Paid Referrals': ref.referrals_paid_count,
                    'Cash Income': ref.cash_income,
                    'Activations': ref.activations_count,
                    'Total Payments': ref.payments_sum,
                    'Average Payment': ref.payments_sum / ref.payments_count if ref.payments_count else 0
                })
    
    df_refs = pd.DataFrame(ref_data)
    for r_idx, row in enumerate(dataframe_to_rows(df_refs, index=False, header=True), 1):
        ws.append(row)
        if r_idx == 1:
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    
    # Summary Sheet
    ws = wb.create_sheet("Summary", 0)  # Make it the first sheet
    summary_data = {
        'Metric': [
            'Total Users',
            'Active Users',
            'Total Categories',
            'Total Active Subscriptions',
            'Total Monthly Revenue',
            'Total Quarterly Revenue',
            'Total Yearly Revenue',
            'Total Overall Revenue',
            'Active Referrers',
            'Total Referral Payments'
        ],
        'Value': [
            len(df_users),
            df_users['Active Subscriptions'].astype(bool).sum(),
            len(df_categories),
            len(df_subs),
            df_financial['Monthly Revenue'].sum(),
            df_financial['Quarterly Revenue'].sum(),
            df_financial['Yearly Revenue'].sum(),
            df_financial['Total Revenue'].sum(),
            len(df_refs),
            df_refs['Total Payments'].sum() if len(df_refs) > 0 else 0
        ]
    }
    
    df_summary = pd.DataFrame(summary_data)
    for r_idx, row in enumerate(dataframe_to_rows(df_summary, index=False, header=True), 1):
        ws.append(row)
        if r_idx == 1:
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    
    # Adjust column widths for all sheets
    for sheet in wb.sheetnames:
        ws = wb[sheet]
        for column in ws.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column[0].column_letter].width = adjusted_width
    
    wb.save(file_path)

