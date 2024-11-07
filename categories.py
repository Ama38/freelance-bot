from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, Message
from sqlalchemy.orm import sessionmaker, joinedload
from models import UsedTrial, engine, User, MessageRecord, Category, ActiveSubscription, SuspendedSubscription
from aiogram import types, Bot, Router, F
from aiogram.filters import Command
import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session as SessionS
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from models import ReferralData
from decimal import Decimal
router_categories = Router()
ADMIN_USER_ID = '5789674670'

CARD_NUMBER = "9999000011112222"
# CATEGORY_DATA = [
#     {"name": "Таргет", "bot_username": "xnoBadVibes"},
#     {"name": "SMM", "bot_username": "xnoBadVibes"},
#     {"name": "Сайты", "bot_username": "xnoBadVibes"},
#     {"name": "SEO", "bot_username": "xnoBadVibes"},
#     {"name": "Дизайн", "bot_username": "xnoBadVibes"},
#     {"name": "Контекст", "bot_username": "xnoBadVibes"},
#     {"name": "Продюсер", "bot_username": "xnoBadVibes"},
#     {"name": "Авитолог", "bot_username": "xnoBadVibes"},
#     {"name": "Юриспреденция", "bot_username": "xnoBadVibes"},
#     {"name": "Психология", "bot_username": "xnoBadVibes"},
#     {"name": "Дизайн Интерьера", "bot_username": "xnoBadVibes"},
#     {"name": "Чат боты", "bot_username": "xnoBadVibes"},
#     {"name": "Копирайтинг", "bot_username": "xnoBadVibes"},
#     {"name": "Ассистент", "bot_username": "xnoBadVibes"},
#     {"name": "Менеджер Маркетплейсов | Вакансии", "bot_username": "xnoBadVibes"},
#     {"name": "Репетитор", "bot_username": "xnoBadVibes"},
#     {"name": "РОП | Вакансии", "bot_username": "xnoBadVibes"},
#     {"name": "Бухгалтерия", "bot_username": "xnoBadVibes"},
#     {"name": "Методолог", "bot_username": "xnoBadVibes"},
#     {"name": "Посевы", "bot_username": "xnoBadVibes"},
#     {"name": "Сертификация", "bot_username": "xnoBadVibes"},
#     {"name": "Пошив одежды", "bot_username": "xnoBadVibes"},
#     {"name": "Рилсмейкер", "bot_username": "xnoBadVibes"},
#     {"name": "Фотограф", "bot_username": "xnoBadVibes"},
#     {"name": "Монтажер", "bot_username": "xnoBadVibes"},
#     {"name": "Продажник", "bot_username": "xnoBadVibes"},
#     {"name": "Бьюти Дубай", "bot_username": "xnoBadVibes"},
# ]

# # Extract just the category names for easier access
# CATEGORIES = [category["name"] for category in CATEGORY_DATA]
CATEGORIES = ['Таргет', 'SMM', 'Сайты', 'SEO', 'Дизайн', 'Контекст', 'Продюсер', 'Авитолог', 'Юриспреденция', 'Психология', 'Дизайн Интерьера', 'Чат боты', 'Копирайтинг', 'Ассистент', 'Менеджер Маркетплейсов | Вакансии', 'Репетитор', 'РОП | Вакансии', 'Бухгалтерия', 'Методолог', 'Посевы', 'Сертификация', 'Пошив одежды', 'Рилсмейкер', 'Фотограф', 'Монтажер', 'Продажник', 'Бьюти Дубай']

async def category_handler(callback: CallbackQuery):
    category_index = int(callback.data.split("_")[1])
    CATEGORIES[category_index-1]


Session = sessionmaker(bind=engine)


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



async def display_all_categories_as_buttons(message: types.Message, bot: Bot):
    session = Session()
    try:
        user = session.query(User).filter(User.chat_id == message.chat.id).first()
        if not user:
            user = User(
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                chat_id=message.chat.id
            )
            session.add(user)
            session.commit()

        all_categories = session.query(Category).options(joinedload(Category.users)).all()
        
        builder = InlineKeyboardBuilder()
        for category in all_categories:
            status = "✅" if user in category.users else "➕"
            builder.button(
                text=f"{status} {category.name}", 
                callback_data=f"category_{category.id}"
            )
        builder.adjust(1)

        await message.answer(
            "Выберите категорию для подписки",
            reply_markup=builder.as_markup()
        )
    finally:
        session.close()

async def handle_category_selection(user: User, category: Category, session: SessionS) -> str:
    if user in category.users:
        return f"Вы уже подписаны на {category.name}"
    else:
        # This is where you would typically initiate the payment process
        # For now, we'll just return a message about the subscription
        return f"You've selected {category.name}. The subscription period is currently set to infinite. Would you like to subscribe?"


# @router_categories.callback_query(lambda c: c.data.startswith('category_'))
# async def process_category_selection(callback_query: types.CallbackQuery):
#     category_id = int(callback_query.data.split('_')[1])
#     session = Session()
#     try:
#         user = session.query(User).filter(User.chat_id == callback_query.from_user.id).first()
#         if not user:
#             await callback_query.answer("User not found. Please start the bot first.")
#             return

#         category = session.query(Category).options(joinedload(Category.users)).filter(Category.id == category_id).first()
#         if not category:
#             await callback_query.answer("Invalid category.")
#             return

#         result = await handle_category_selection(user, category, session)
        
#         # Create confirmation buttons
#         builder = InlineKeyboardBuilder()
#         if user in category.users:
#             builder.button(text="Unsubscribe", callback_data=f"unsubscribe_{category.id}")
#         else:
#             builder.button(text="Subscribe", callback_data=f"subscribe_{category.id}")
#         builder.button(text="Cancel", callback_data="cancel")
        
#         await callback_query.message.answer(result, reply_markup=builder.as_markup())
#     finally:
#         session.close()
#     await callback_query.answer()


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
    resize_keyboard=True
)


class PaymentStates(StatesGroup):
    waiting_for_payment = State()

@router_categories.callback_query(lambda c: c.data.startswith("category_"))
async def process_category_selection(callback_query: types.CallbackQuery):
    category_id = int(callback_query.data.split('_')[1])
    session = Session()
    try:
        user = session.query(User).filter(User.chat_id == callback_query.from_user.id).first()
        if not user:
            await callback_query.answer("Пользователь не найден, пожалуйста запустите бота")
            return
        
        category = session.query(Category).options(
            joinedload(Category.users),
            joinedload(Category.used_trials)
        ).filter(Category.id == category_id).first()
        
        if not category:
            await callback_query.answer("Неверная категория")
            return
        
        if session.query(ActiveSubscription).filter(
            ActiveSubscription.user_id == user.id,
            ActiveSubscription.category_id == category.id
        ).first():
            await callback_query.answer("Уже имеется активная подписка на категорию")
            return
        
        if session.query(SuspendedSubscription).filter(
            SuspendedSubscription.user_id == user.id,
            SuspendedSubscription.category_id == category.id
        ).first():
            await callback_query.answer("Уже имеется замороженная подписка на категорию")
            return

        builder = InlineKeyboardBuilder()
        
        # Add trial button if available
        has_used_trial = session.query(UsedTrial).filter(
            UsedTrial.user_id == user.id,
            UsedTrial.category_id == category.id
        ).first()
        
        if category.has_3_days_free and not has_used_trial:
            builder.button(
                text="Пробный период (3 дня бесплатно)",
                callback_data=f"trial_{category.id}"
            )

        # Monthly subscription button
        builder.button(
            text=f"Ежемесячная подписка: {category.price_monthly} руб/мес",
            callback_data=f"price_{category.id}_1"
        )
        
        # Quarterly subscription button
        builder.button(
            text=f"Квартальная подписка: {category.price_quarterly} руб/3 мес",
            callback_data=f"price_{category.id}_3"
        )
        
        # Half-yearly subscription button
        builder.button(
            text=f"Полугодовая подписка: {category.price_half_yearly} руб/6 мес",
            callback_data=f"price_{category.id}_6"
        )
        
        # Yearly subscription button
        builder.button(
            text=f"Годовая подписка: {category.price_yearly} руб/год",
            callback_data=f"price_{category.id}_12"
        )
        
        builder.button(text="Отмена", callback_data="cancel")
        
        builder.adjust(1)
        await callback_query.message.answer(
            text="Выберите длительность подписки:", 
            reply_markup=builder.as_markup()
        )
        
    finally:
        session.close()
    await callback_query.answer()


class PaymentStates(StatesGroup):
    waiting_for_payment_method = State()
    waiting_for_card_payment = State()

@router_categories.callback_query(F.data.startswith("price_"))
async def process_subscription_selection(callback_query: CallbackQuery, state: FSMContext):
    _, category_id, months = callback_query.data.split('_')
    category_id = int(category_id)
    months = int(months)
    session = Session()
    try:
        user = session.query(User).options(joinedload(User.referral_data)).filter(User.chat_id == callback_query.from_user.id).first()
        if not user:
            await callback_query.answer("Пользователь не найден, пожалуйста запустите бота")
            return
        category = session.query(Category).filter(Category.id == category_id).first()
        if not category:
            await callback_query.answer("Неверная категория")
            return
        
        # Calculate subscription details based on months
        if months == 1:
            price = category.price_monthly
            subscription_type = "monthly"
            duration_text = "1 месяц"
        elif months == 3:
            price = category.price_quarterly
            subscription_type = "quarterly"
            duration_text = "3 месяца"
        elif months == 6:
            price = category.price_half_yearly
            subscription_type = "half_yearly"
            duration_text = "6 месяцев"
        elif months == 12:
            price = category.price_yearly
            subscription_type = "yearly"
            duration_text = "1 год"
        else:
            await callback_query.answer("Неверный период подписки.")
            return

        # Store subscription details in FSM context
        await state.update_data(
            category_id=category_id,
            months=months,
            price=price,
            subscription_type=subscription_type
        )

        # Check if user has enough referral balance
        referral_balance = user.referral_data.referral_balance if user.referral_data else 0
       
        # Create payment method buttons
        buttons = []
        if referral_balance >= price:
            buttons.append([InlineKeyboardButton(text="Оплатить реферальным счетом", callback_data="pay_referral")])
        buttons.append([InlineKeyboardButton(text="Оплатить картой", callback_data="pay_card")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await callback_query.message.answer(
            f"Детали подписки:\n"
            f"Категория: {category.name}\n"
            f"Длительность: {duration_text}\n"
            f"Цена: {price} руб\n"
            f"Ваш реферальный баланс: {referral_balance} руб\n\n"
            f"Пожалуйста выберите способ оплаты:",
            reply_markup=keyboard
        )
        await state.set_state(PaymentStates.waiting_for_payment_method)
    except Exception as e:
        logging.error(f"Error processing subscription selection: {e}")
        await callback_query.answer("Произошла ошибка при обработке подписки")
    finally:
        session.close()
        
        
        
@router_categories.callback_query(lambda c: c.data.startswith("trial_"))
async def process_trial_selection(callback_query: CallbackQuery, state: FSMContext):
    _, category_id = callback_query.data.split('_')
    category_id = int(category_id)
    session = Session()
    try:
        user = session.query(User).filter(User.chat_id == callback_query.from_user.id).first()
        category = session.query(Category).filter(Category.id == category_id).first()
        
        if not all([user, category]):
            await callback_query.answer("Ошибка: пользователь или категория не найдены")
            return

        # Record trial usage
        new_trial = UsedTrial(
            user_id=user.id,
            category_id=category_id
        )
        session.add(new_trial)
        
        # Calculate trial period dates
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=3)
        
        # Create trial subscription
        new_subscription = ActiveSubscription(
            user_id=user.id,
            category_id=category_id,
            start_date=start_date,
            end_date=end_date,
            subscription_type='trial'
        )
        session.add(new_subscription)
        session.commit()

        await callback_query.message.edit_text(
            f"Пробный период активирован!\n"
            f"Категория: {category.name}\n"
            f"Начало: {start_date.strftime('%d.%m.%Y')}\n"
            f"Окончание: {end_date.strftime('%d.%m.%Y')}\n\n"
            "Хорошего пользования!"
        )
        await state.clear()

    except Exception as e:
        logging.error(f"Error processing trial: {e}")
        await callback_query.answer("Произошла ошибка при активации пробного периода")
        await state.clear()
    finally:
        session.close()

@router_categories.callback_query(PaymentStates.waiting_for_payment_method)
async def process_payment_method(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback_query.from_user.id
    session = Session()
    try:
        user = session.query(User).options(joinedload(User.referral_data)).filter(User.chat_id == user_id).first()
        if not user:
            await callback_query.answer("Пользователь не найден, пожалуйста запустите бота")
            return

        data = await state.get_data()
        category_id = data['category_id']
        price = data['price']
        subscription_type = data['subscription_type']
        months = data['months']

        category = session.query(Category).filter(Category.id == category_id).first()

        if callback_query.data == "pay_referral":
            if user.referral_data and user.referral_data.referral_balance >= price:

                user.referral_data.referral_balance -= price
                await create_subscription(user, category, subscription_type, months, session)
                await bot.send_message(user_id, f"Сумма в {price} руб была списана с вашего реферального баланса. Ваша подписка успешно активирована")
                await state.clear()
            else:
                await callback_query.answer("Недостаточно средств на реферальном балансе. Пожалуйста выберите другой способ оплаты.")
        elif callback_query.data == "pay_card":
            await bot.send_message(
                user_id,
                f"Пожалуйста оплатите сумму {price} руб по следующему номеру карты:\n\n"
                f"{CARD_NUMBER}\n\n"
                "После процесса оплаты, пожалуйста отправьте снимок экрана с чеком в этот чат."
            )
            await state.set_state(PaymentStates.waiting_for_card_payment)
        else:
            await callback_query.answer("Invalid payment method selected.")

    except Exception as e:
        await callback_query.answer(f"An error occurred: {str(e)}")
    finally:
        session.close()

async def create_subscription(user, category, subscription_type, months, session):
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=30 * months)

    new_subscription = ActiveSubscription(
        user_id=user.id,
        category_id=category.id,
        start_date=start_date,
        end_date=end_date,
        subscription_type=subscription_type
    )
    session.add(new_subscription)

    if user not in category.users:
        category.users.append(user)

    session.commit()

@router_categories.message(PaymentStates.waiting_for_card_payment, F.photo)
async def process_payment_confirmation(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    session = Session()
    try:
        user = session.query(User).filter(User.chat_id == user_id).first()
        if not user:
            await message.answer("Пользователь не найден, пожалуйста запустите бота")
            return

        # Get subscription details from FSM context
        data = await state.get_data()
        category_id = data['category_id']
        months = data['months']
        price = data['price']
        subscription_type = data['subscription_type']

        category = session.query(Category).filter(Category.id == category_id).first()

        # Forward the image to admin
        admin_message = await bot.send_photo(
            ADMIN_USER_ID,
            message.photo[-1].file_id,
            caption=f"Подтверждение платежа:\n Пользователь: {user.username} (ID: {user.id})\n"
                    f"Категория: {category.name}\n Цена: {price} руб\n"
                    f"Длительность: {months} month(s)\n Тип подписки: {subscription_type}"
        )

        # Add approval buttons for admin
        approval_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Одобрить", callback_data=f"app_{user.id}_{category.id}_{subscription_type}_{months}"),
                InlineKeyboardButton(text="Отклонить", callback_data=f"rej_{user.id}_{category.id}")
            ]
        ])
        await bot.send_message(ADMIN_USER_ID, "Вы одобряете этот платеж?", reply_markup=approval_keyboard)

        await message.answer("Информация о платеже была передана администрации. Пожалуйста дождитесь подтверждения.")
        await state.clear()

    except Exception as e:
        await message.answer(f"An error occurred: {str(e)}")
    finally:
        session.close()

@router_categories.callback_query(F.data.startswith("app_"))
async def approve_payment(callback_query: CallbackQuery, bot: Bot):
    _, user_id, category_id, subscription_type, months = callback_query.data.split('_')
    user_id = int(user_id)
    category_id = int(category_id)
    months = int(months)
    session = Session()
    try:
        user = session.query(User).options(joinedload(User.referred_by)).filter(User.id == user_id).first()
        category = session.query(Category).filter(Category.id == category_id).first()

        if not user or not category:
            await callback_query.answer("Пользователь не найден, пожалуйста запустите бота")
            return

        if months == 1:
            price = category.price_monthly
        elif months == 3:
            price = category.price_quarterly
        elif months == 12:
            price = category.price_yearly
        else:
            await callback_query.answer("Invalid subscription period.")
            return

        new_subscription = await create_subscription(user, category, subscription_type, months, session)

        # Handle referral system updates
        if user.referred_by:
            referrer = user.referred_by
            referrer_data = referrer.referral_data
            if not referrer_data:
                referrer_data = ReferralData(user=referrer)
                session.add(referrer_data)

            # Increase referral balance by 10% of payment
            referral_commission = price * 0.1
            referrer_data.referral_balance += referral_commission

            # Update referral statistics
            referrer_data.referrals_paid_count += 1
            referrer_data.people_paid_count += 1
            referrer_data.payments_count += 1
            referrer_data.payments_sum += price

            await bot.send_message(referrer.chat_id, 
                                   f"Ваш реферал произвел оплату. "
                                   f"На ваш реферальный счет было начислено {referral_commission:.2f} руб.")

        session.commit()
        await bot.send_message(user.chat_id, f"Ваша подписка на {category.name} была одобрена и активирована!")
        if category.bot_token:
            message = (
                f"Пожалуйста напишите нашему боту чтобы начать получать новые сообщения "
                f"@{category.bot_username}"
            )
        else:
            message = "Вы будете получать сообщения в текущем боте"
    
        await bot.send_message(user.chat_id, message, reply_markup=keyboard_registered)
        await callback_query.answer("Payment approved and subscription activated.")

    except Exception as e:
        await callback_query.answer(f"An error occurred: {str(e)}")
        session.rollback()
    finally:
        session.close()

@router_categories.callback_query(F.data.startswith("rej_"))
async def reject_payment(callback_query: CallbackQuery, bot: Bot):
    _, user_id, category_id = callback_query.data.split('_')
    user_id = int(user_id)
    category_id = int(category_id)

    session = Session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        category = session.query(Category).filter(Category.id == category_id).first()

        await bot.send_message(user.chat_id, f"Ваша оплата не была одобрена по категории {category.name}. Пожалуйста свяжитесь с поддержкой если у вас есть вопросы.")
        await callback_query.answer("Payment rejected.")

    except Exception as e:
        await callback_query.answer(f"An error occurred: {str(e)}")
    finally:
        session.close()




@router_categories.callback_query(lambda c: c.data.startswith('subscribe_'))
async def process_subscription(callback_query: types.CallbackQuery):
    category_id = int(callback_query.data.split('_')[1])
    session = Session()
    try:
        user = session.query(User).filter(User.chat_id == callback_query.from_user.id).first()
        category = session.query(Category).options(joinedload(Category.users)).filter(Category.id == category_id).first()
        
        if user and category:
            if user not in category.users:
                category.users.append(user)
                session.commit()
                await callback_query.message.answer(f"You've been subscribed to {category.name}. Your subscription is set to infinite.")
            else:
                await callback_query.message.answer(f"You're already subscribed to {category.name}.")
        else:
            await callback_query.message.answer("An error occurred. Please try again.")
    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Error in process_subscription: {str(e)}")
        await callback_query.message.answer("An error occurred while processing your request.")
    finally:
        session.close()
    await callback_query.answer()

@router_categories.callback_query(lambda c: c.data.startswith('unsubscribe_'))
async def process_unsubscription(callback_query: types.CallbackQuery):
    category_id = int(callback_query.data.split('_')[1])
    session = Session()
    try:
        user = session.query(User).filter(User.chat_id == callback_query.from_user.id).first()
        category = session.query(Category).options(joinedload(Category.users)).filter(Category.id == category_id).first()
        
        if user and category:
            if user in category.users:
                category.users.remove(user)
                session.commit()
                await callback_query.message.answer(f"You've been unsubscribed from {category.name}.")
            else:
                await callback_query.message.answer(f"You're not subscribed to {category.name}.")
        else:
            await callback_query.message.answer("An error occurred. Please try again.")
    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Error in process_unsubscription: {str(e)}")
        await callback_query.message.answer("An error occurred while processing your request.")
    finally:
        session.close()
    await callback_query.answer()

@router_categories.callback_query(lambda c: c.data == 'cancel')
async def process_cancel(callback_query: types.CallbackQuery, bot: Bot):
    await display_all_categories_as_buttons(callback_query.message, bot)
    await callback_query.answer()
    

@router_categories.message(F.text == "🤑 Категории заявок")
async def cmd_subscribe(message: types.Message, bot: Bot):
    await display_all_categories_as_buttons(message, bot)






