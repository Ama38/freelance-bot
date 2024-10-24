from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from message_scraper import Session, User
from aiogram.filters.state import StateFilter
import logging
from typing import Union
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from admin import is_admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BroadcastStates(StatesGroup):
    waiting_for_message = State()
    confirm_broadcast = State()


router_broadcast = Router()

async def copy_message_content(msg: Message, target_chat_id: Union[int, str]) -> bool:
    """
    Copy message content to target chat without forwarding
    Returns True if successful, False otherwise
    """
    try:
        if msg.text:
            await msg.bot.send_message(
                chat_id=target_chat_id,
                text=msg.text,
                entities=msg.entities
            )
        elif msg.photo:
            await msg.bot.send_photo(
                chat_id=target_chat_id,
                photo=msg.photo[-1].file_id,
                caption=msg.caption,
                caption_entities=msg.caption_entities
            )
        elif msg.video:
            await msg.bot.send_video(
                chat_id=target_chat_id,
                video=msg.video.file_id,
                caption=msg.caption,
                caption_entities=msg.caption_entities
            )
        elif msg.audio:
            await msg.bot.send_audio(
                chat_id=target_chat_id,
                audio=msg.audio.file_id,
                caption=msg.caption,
                caption_entities=msg.caption_entities
            )
        elif msg.voice:
            await msg.bot.send_voice(
                chat_id=target_chat_id,
                voice=msg.voice.file_id,
                caption=msg.caption,
                caption_entities=msg.caption_entities
            )
        elif msg.document:
            await msg.bot.send_document(
                chat_id=target_chat_id,
                document=msg.document.file_id,
                caption=msg.caption,
                caption_entities=msg.caption_entities
            )
        elif msg.sticker:
            await msg.bot.send_sticker(
                chat_id=target_chat_id,
                sticker=msg.sticker.file_id
            )
        elif msg.animation:
            await msg.bot.send_animation(
                chat_id=target_chat_id,
                animation=msg.animation.file_id,
                caption=msg.caption,
                caption_entities=msg.caption_entities
            )
        else:
            logger.error(f"Unsupported message type: {msg.content_type}")
            return False
        return True
    except Exception as e:
        logger.error(f"Error copying message: {str(e)}")
        return False



@router_broadcast.message(Command("broadcast"))
async def cmd_broadcast(message:Message, state:FSMContext) -> None:
    if is_admin(message.from_user.id):
        await message.answer(
            "Пожалуйста отправьте сообщение которое вы ходите распространить\n"
            "Это может быть как текст так и что угодно еще\n"
            "Отправьте /cancel чтобы отменить операцию"
        )

        await state.set_state(BroadcastStates.waiting_for_message)
    logger.error("Not admin")


@router_broadcast.message(StateFilter(BroadcastStates.waiting_for_message))
async def process_broadcast_message(message:Message, state: FSMContext) -> None:
    await state.update_data(
        message=message,
        chat_id=message.chat.id,
        message_type=message.content_type
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data="broadcast_confirm")
    builder.button(text="❌ Отменить", callback_data="broadcast_cancel")

    await message.answer(
        "Пожалуйста подтвердите рассылку сообщения всем:",
        reply_markup=builder.as_markup()
    )


    await message.forward(message.chat.id)

    
    await state.set_state(BroadcastStates.confirm_broadcast)


@router_broadcast.callback_query(lambda c: c.data.startswith('broadcast_'))
async def process_broadcast_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback_query.from_user.id):
        return
    
    action = callback_query.data.split("_")[1]

    if action == 'cancel':
        await state.clear()
        await callback_query.message.edit_text("Рассылка отменена")
        return
    
    if action == "confirm":
        data = await state.get_data()
        original_message = data['message']


        await callback_query.message.edit_text("Рассылаем сообщение всем пользователям...")

        session = Session()

        try:
            users = session.query(User).all()

            successful = 0
            failed = 0

            for user in users:
                try:
                    if await copy_message_content(original_message, user.chat_id):
                        successful += 1
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1
                    logger.error(f"Failed to send message to {user.chat_id}: {str(e)}")


            await callback_query.message.edit_text(
                f"Broadcast completed!\n"
                f"✅ Successfully sent: {successful}\n"
                f"❌ Failed: {failed}\n"
                f"📊 Total users: {len(users)}"
            )               

        except Exception as e:
            await callback_query.message.edit_text(
                f"Error during broadcast: {str(e)}"
            )
        finally:
            session.close()
            await state.clear()


@router_broadcast.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    """Handler for /cancel command"""
    current_state = await state.get_state()
    if current_state is None:
        return
    
    await state.clear()
    await message.answer("Broadcast cancelled.")


                    