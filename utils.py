from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import types, Bot, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
from sqlalchemy.orm import Session
from models import engine, Category
from sqlalchemy import text
from admin import admin_only
router_utils = Router()




class AddCategoryForm(StatesGroup):
    name = State()
    keywords = State()
    price_monthly = State()
    price_quarterly = State()
    price_yearly = State()
    bot_token = State()
    bot_username = State()


@router_utils.message(Command("add_category"))
@admin_only
async def add_category(message: Message, state: FSMContext):
    await state.set_state(AddCategoryForm.name)
    await message.answer("Давайте добавим новую категорию. Пожалуйста, введите название категории:")


@router_utils.message(F.text.lower() == "cancel")
@admin_only
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Процесс добавления категории отменен.")


@router_utils.message(AddCategoryForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddCategoryForm.keywords)
    await message.answer("Отлично! Теперь введите ключевые слова для этой категории, разделенные запятыми:")

@router_utils.message(AddCategoryForm.keywords)
async def process_keywords(message: Message, state: FSMContext):
    keywords = message.text.strip()
    await state.update_data(keywords=keywords)
    await state.set_state(AddCategoryForm.price_monthly)
    await message.answer("Ключевые слова добавлены. Теперь введите месячную стоимость подписки для этой категории (в рублях):")

@router_utils.message(AddCategoryForm.price_monthly)
async def process_price_monthly(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price_monthly=price)
        await state.set_state(AddCategoryForm.price_quarterly)
        await message.answer("Введите квартальную стоимость подписки для этой категории (в рублях):")
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число для стоимости.")

@router_utils.message(AddCategoryForm.price_quarterly)
async def process_price_quarterly(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price_quarterly=price)
        await state.set_state(AddCategoryForm.price_yearly)
        await message.answer("Наконец, введите годовую стоимость подписки для этой категории (в рублях):")
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число для стоимости.")

@router_utils.message(AddCategoryForm.price_yearly)
async def process_price_yearly(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price_yearly=price)
        
        # Create inline keyboard with Yes/No buttons
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data="add_bot_yes"),
                InlineKeyboardButton(text="Нет", callback_data="add_bot_no")
            ]
        ])
        
        await message.answer(
            "Хотите добавить бота для этой категории?",
            reply_markup=keyboard
        )
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число для стоимости.")

@router_utils.callback_query(F.data.startswith("add_bot_"))
async def process_bot_confirmation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    if callback.data == "add_bot_no":
        # Save category without bot
        data = await state.get_data()
        await save_category(callback.message, state, data)
    else:
        await state.set_state(AddCategoryForm.bot_token)
        await callback.message.answer("Пожалуйста, отправьте токен бота:")
    
    # Remove the inline keyboard
    await callback.message.edit_reply_markup(reply_markup=None)

@router_utils.message(AddCategoryForm.bot_token)
async def process_bot_token(message: Message, state: FSMContext):
    await state.update_data(bot_token=message.text)
    await state.set_state(AddCategoryForm.bot_username)
    await message.answer("Теперь отправьте username бота (без @):")


@router_utils.message(AddCategoryForm.bot_username)
async def process_bot_username(message: Message, state: FSMContext):
    username = message.text.lstrip('@')  # Remove @ if present
    await state.update_data(bot_username=username)
    
    data = await state.get_data()
    await save_category(message, state, data)


async def save_category(message: Message, state: FSMContext, data: dict):
    try:
        with Session(engine) as session:
            new_category = Category(
                name=data['name'],
                keywords=data['keywords'],
                price_monthly=data['price_monthly'],
                price_quarterly=data['price_quarterly'],
                price_yearly=data['price_yearly'],
                bot_token=data.get('bot_token'),
                bot_username=data.get('bot_username')
            )
            session.add(new_category)
            session.commit()
        
        response = (f"Категория '{data['name']}' успешно добавлена со следующими данными:\n"
                   f"Ключевые слова: {data['keywords']}\n"
                   f"Месячная подписка: {data['price_monthly']} руб.\n"
                   f"Квартальная подписка: {data['price_quarterly']} руб.\n"
                   f"Годовая подписка: {data['price_yearly']} руб.")
        
        if data.get('bot_token'):
            response += f"\nБот: @{data['bot_username']}"

        await message.answer(response)
        await state.clear()
    except Exception as e:
        logging.error(f"Error saving category: {e}")
        await message.answer("Произошла ошибка при сохранении категории. Пожалуйста, попробуйте позже.")
        await state.clear()




@router_utils.message(Command("add_category"))
@admin_only
async def add_category(message: Message, state: FSMContext):
    await state.set_state(AddCategoryForm.name)
    await message.answer("Давайте добавим новую категорию. Пожалуйста, введите название категории:")


@router_utils.message(F.text.lower() == "cancel")
@admin_only
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Процесс добавления категории отменен.")


@router_utils.message(AddCategoryForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddCategoryForm.keywords)
    await message.answer("Отлично! Теперь введите ключевые слова для этой категории, разделенные запятыми:")

@router_utils.message(AddCategoryForm.keywords)
async def process_keywords(message: Message, state: FSMContext):
    keywords = message.text.strip()
    await state.update_data(keywords=keywords)
    await state.set_state(AddCategoryForm.price_monthly)
    await message.answer("Ключевые слова добавлены. Теперь введите месячную стоимость подписки для этой категории (в рублях):")

@router_utils.message(AddCategoryForm.price_monthly)
async def process_price_monthly(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price_monthly=price)
        await state.set_state(AddCategoryForm.price_quarterly)
        await message.answer("Введите квартальную стоимость подписки для этой категории (в рублях):")
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число для стоимости.")

@router_utils.message(AddCategoryForm.price_quarterly)
async def process_price_quarterly(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price_quarterly=price)
        await state.set_state(AddCategoryForm.price_yearly)
        await message.answer("Наконец, введите годовую стоимость подписки для этой категории (в рублях):")
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число для стоимости.")

@router_utils.message(AddCategoryForm.price_yearly)
async def process_price_yearly(message: Message, state: FSMContext):

    try:
        price = float(message.text)
        await state.update_data(price_yearly=price)
        
        # Get all the collected data
        data = await state.get_data()
        
        
        with Session(engine) as session:
            new_category = Category(
                name=data['name'],
                keywords=data['keywords'],
                price_monthly=data['price_monthly'],
                price_quarterly=data['price_quarterly'],
                price_yearly=data['price_yearly']
            )
            session.add(new_category)
            session.commit()
        
        await message.answer(f"Категория '{data['name']}' успешно добавлена со следующими данными:\n"
                             f"Ключевые слова: {data['keywords']}\n"
                             f"Месячная подписка: {data['price_monthly']} руб.\n"
                             f"Квартальная подписка: {data['price_quarterly']} руб.\n"
                             f"Годовая подписка: {data['price_yearly']} руб.")
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число для стоимости.")

def useful_info(message: Message):

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Канал с обновлениями", url="https://t.me/your_channel"))
    builder.add(InlineKeyboardButton(text="Чат поддержки", url="https://t.me/your_support_chat"))
    builder.add(InlineKeyboardButton(text="Подробнее о боте", callback_data="bot_info"))
    builder.adjust(1)
    return builder.as_markup()



@router_utils.callback_query(F.data == "bot_info")
async def bot_info_handler(callback_query: CallbackQuery):
    info_text = (
        "Бот парсит чаты по ключевым словам и переслывает сообщения от потенциальных клиентов. \n\n\n"
        "Пример: \"Ищу таргетолога\", \"ищу дизайнера\" и др. Все что вам остается - это написать человеку на его запрос.\n\n\n"
        "Заявки берутся из открытых источников, чаты, каналы, а также сторонние сайты.\n\n\n"
        "В боте есть 11 направлений. По кнопке \"Категории заявок\" вы можете выбрать нужную категорию. \n\n\n"
        "Подбирать свои ключевые слова пока нельзя. Выбирать можно только из готовых категорий."
    )
    
    await callback_query.message.answer(info_text)
    await callback_query.answer()



SUPPORT_CHAT_ID = -1001234567890 


class SupportStates(StatesGroup):
    waiting_for_message = State()

@router_utils.message(Command("support"))
@admin_only
async def cmd_support(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, опишите вашу проблему или задайте вопрос. Мы постараемся помочь вам как можно скорее.\n\nЕсли вы хотите отменить запрос в поддержку, отправьте /cancel.")
    await state.set_state(SupportStates.waiting_for_message)

@router_utils.message(Command("cancel"), StateFilter(SupportStates.waiting_for_message))
@admin_only
async def cancel_support(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Запрос в поддержку отменен. Если у вас возникнут вопросы в будущем, не стесняйтесь обращаться.")

@router_utils.message(StateFilter(SupportStates.waiting_for_message))
async def process_support_message(message: Message, state: FSMContext):
    if message.text.lower() == '/cancel':
        await cancel_support(message, state)
        return

    user_message = message.text
    username = message.from_user.username or "Unknown"
    user_id = message.from_user.id
    
    support_message = f"Новое сообщение в поддержку:\n\nID: {user_id}\nUsername: @{username}\n\nСообщение:\n{user_message}"
        

    #await message.bot.send_message(SUPPORT_CHAT_ID, support_message)
    print(support_message)
    await message.answer("Спасибо за ваше сообщение. Наша команда поддержки свяжется с вами в ближайшее время.")
    
    await state.clear()

def support_chat(message: Message, state: FSMContext):
    return cmd_support(message, state)




def setup_message_retention(engine):
    with engine.connect() as conn:
        conn.execute(text("DROP TRIGGER IF EXISTS cleanup_messages"))

        trigger_sql = """
        CREATE TRIGGER cleanup_messages
        AFTER INSERT ON messages
        BEGIN
            DELETE FROM messages 
            WHERE created_at < datetime('now', '-3 days');
        END;
        """
        conn.execute(text(trigger_sql))
        conn.commit()
        print("Added retention trigger to messages table")






@router_utils.message(Command("delete_category"))
@admin_only
async def delete_category_start(message: Message):
    with Session(engine) as session:
        categories = session.query(Category).all()
        if not categories:
            await message.answer("Нет доступных категорий для удаления.")
            return

        # Create inline keyboard with one button per row
        buttons = []
        for cat in categories:
            button_text = f"{cat.name} - {cat.price_monthly}₽/мес"
            if cat.bot_username:
                button_text += f" (@{cat.bot_username})"
            buttons.append([InlineKeyboardButton(
                text=button_text, 
                callback_data=f"select_category_{cat.id}"
            )])

        # Add cancel button at the bottom
        buttons.append([InlineKeyboardButton(
            text="Отмена", 
            callback_data="cancel_delete"
        )])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await message.answer(
            "Выберите категорию для удаления:",
            reply_markup=keyboard
        )

@router_utils.callback_query(F.data.startswith("select_category_"))
async def category_selected(callback: CallbackQuery):
    await callback.answer()
    category_id = int(callback.data.split('_')[2])
    
    try:
        with Session(engine) as session:
            category = session.query(Category).filter(Category.id == category_id).first()
            if not category:
                await callback.message.edit_text("Категория не найдена.")
                return

            # Create confirmation keyboard
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Подтвердить", callback_data=f"delete_category_{category_id}"),
                    InlineKeyboardButton(text="Отмена", callback_data="cancel_delete")
                ]
            ])

            category_info = (
                f"Категория: {category.name}\n"
                f"Ключевые слова: {category.keywords}\n"
                f"Цены:\n"
                f"- Месяц: {category.price_monthly}₽\n"
                f"- Квартал: {category.price_quarterly}₽\n"
                f"- Год: {category.price_yearly}₽\n"
            )
            
            if category.bot_username:
                category_info += f"Бот: @{category.bot_username}\n"

            await callback.message.edit_text(
                f"{category_info}\n\nВы уверены, что хотите удалить эту категорию?\n"
                "Это действие нельзя отменить, и все подписки на эту категорию будут удалены.",
                reply_markup=keyboard
            )
    
    except Exception as e:
        logging.error(f"Error in category selection: {e}")
        await callback.message.edit_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

@router_utils.callback_query(F.data.startswith("delete_category_"))
async def confirm_delete_category(callback: CallbackQuery):
    await callback.answer()
    
    try:
        category_id = int(callback.data.split('_')[2])
        
        with Session(engine) as session:
            category = session.query(Category).filter(Category.id == category_id).first()
            if category:
                category_name = category.name
                session.delete(category)
                session.commit()
                
                await callback.message.edit_text(
                    f"Категория '{category_name}' была успешно удалена.",
                    reply_markup=None
                )
            else:
                await callback.message.edit_text("Категория не найдена.")
    
    except Exception as e:
        logging.error(f"Error deleting category: {e}")
        await callback.message.edit_text("Произошла ошибка при удалении категории.")

@router_utils.callback_query(F.data == "cancel_delete")
async def cancel_delete_category(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("Удаление категории отменено.")
