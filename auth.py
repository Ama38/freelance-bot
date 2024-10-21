import logging 
import os
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
import redis 
import json
from dotenv import load_dotenv


load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



if "AMVERA" in os.environ:
    redis_host = 'amvera-salyev-run-freelance-bot-redis'
    redis_port = 6379
else:
    redis_host = 'localhost'
    redis_port = 6379


r = redis.Redis(host=redis_host, port=redis_port, db=0)


telethon_router = Router()


class TelethonAuthForm(StatesGroup):
    waiting_for_code = State()
    waiting_for_password = State()


@telethon_router.message(Command("auth"))
async def auth_command(message: Message, state: FSMContext):
    await state.set_state(TelethonAuthForm.waiting_for_code)
    await message.reply("Please enter the authentication code you received:")

@telethon_router.message(Command('done'))
async def finish_auth(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state in [TelethonAuthForm.waiting_for_code, TelethonAuthForm.waiting_for_password]:
        await state.clear()
        await message.reply("Authentication process completed. Thank you!")
    else:
        await message.reply("No active authentication process.")


@telethon_router.message(TelethonAuthForm.waiting_for_code)
async def process_code(message: Message, state: FSMContext):
    await state.update_data(code=message.text)

    r.set('auth_code', message.text)
    await message.reply("Code received. If two-step verification is enabled, please enter your password. Otherwise, use /done to finish authentication.")
    await state.set_state(TelethonAuthForm.waiting_for_password)

@telethon_router.message(TelethonAuthForm.waiting_for_password)
async def process_password(message: Message, state:FSMContext):
    r.set("auth_password", message.text)
    await message.reply("Password received. Use /done to finish authentication.")



