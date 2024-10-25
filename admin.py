from aiogram.types import Message
from aiogram.filters import BaseFilter, Command
from sqlalchemy import select, update, delete 
from functools import wraps
from models import Session, Admin
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import F, Router, types



router_admin = Router()



def is_admin(user_id:int) -> bool:
    if user_id == 635042713:
        return True
    
    with Session() as session:
        query = select(Admin).where(Admin.telegram_id == user_id)
        result = session.query(query)
        return result.scalar_one_or_none() is not None
    


def admin_only(func):
    @wraps(func)
    async def wrapper(message: Message, **kwargs):
        if not is_admin(message.from_user.id):
            return
        return await func(message, **kwargs)
    return wrapper


class AdminManagement(StatesGroup):
    add_get_id = State()

    delete_confirm = State()

    edit_select_admin = State()
    edit_select_field = State()
    edit_get_value = State()


@router_admin.message(Command('add_admin'))
@admin_only
async def add_admin_start(message:Message, state:FSMContext):
    await message.answer("Пожалуйста перешлите сообщение от пользователя или отправьте их Telegram ID")
    await state.set_state(AdminManagement.add_get_id)


@router_admin.message(AdminManagement.add_get_id)
async def add_admin_process(message:Message, state:FSMContext):
    if message.forward_from.id:
        user = message.forward_from
        user_id = user.id
        # Safely get optional fields
        username = getattr(user, 'username', None)
        first_name = getattr(user, 'first_name', None)
        last_name = getattr(user, 'last_name', None)
    else:
        try:
            user_id = int(message.text)
            username = None
            first_name = None
            last_name = None
        except ValueError:
            await message.answer("Пожалуйста отправьте валидный Telegram ID или пересланное сообщение")
            return        

    with Session() as session:
        existing_admin = session.execute(
            select(Admin).where(Admin.telegram_id == user_id)
        ).scalar_one_or_none()

        if existing_admin:
            await message.answer("Пользователь уже админ")
            await state.clear()
            return
        
        new_admin = Admin(telegram_id=user_id)

        if username:
            new_admin.username = username
        if first_name:
            new_admin.first_name = first_name
        if last_name:
            new_admin.last_name = last_name

        session.add(new_admin)
        session.commit()

    await message.answer("Админ успешно создан")
    await state.clear()

@router_admin.message(Command('list_admins'))
@admin_only
async def list_admins(message: Message):
    with Session() as session:
        admins = session.execute(select(Admin)).scalars().all()

    if not admins:
        await message.answer("Админов нет")
        return 
    
    admin_list = []
    for admin in admin_list:
        admin_info = [f"ID: {admin.telegram_id}"]
        if admin.username:
            admin_info.append(f"Username: @{admin.username}")
        if admin.first_name or admin.last_name:
            name_parts = []
            if admin.first_name:
                name_parts.append(admin.first_name)
            if admin.last_name:
                name_parts.append(admin.last_name)
            admin_info.append(f"Name: {' '.join(name_parts)}")
        admin_list.append("\n".join(admin_info))

    await message.answer(
        "Текущие админы:\n\n" + 
        "\n\n".join(admin_list)
    )
        

@router_admin.message(Command("delete_admin"))
@admin_only
async def delete_admin_start(message: types.Message, state: FSMContext):
    with Session() as session:
        admins = session.execute(select(Admin)).scalars().all()
        
    if not admins:
        await message.answer("No admins to delete!")
        return
        
    admin_list = []
    for admin in admins:
        admin_info = [f"ID: {admin.telegram_id}"]
        if admin.username:
            admin_info.append(f"@{admin.username}")
        admin_list.append(" - ".join(admin_info))
    
    await message.answer(
        "Current admins:\n" +
        "\n".join(admin_list) +
        "\n\nSend the Telegram ID of the admin you want to delete, or 'cancel' to abort."
    )
    await state.set_state(AdminManagement.delete_confirm)

@router_admin.message(AdminManagement.delete_confirm)
async def delete_admin_confirm(message: types.Message, state: FSMContext):
    if message.text.lower() == 'cancel':
        await message.answer("Operation cancelled.")
        await state.clear()
        return
        
    try:
        admin_id = int(message.text)
    except ValueError:
        await message.answer("Please send a valid Telegram ID or 'cancel'.")
        return
        
    with Session() as session:
        admin = session.execute(
            select(Admin).where(Admin.telegram_id == admin_id)
        ).scalar_one_or_none()
        
        if not admin:
            await message.answer("Admin not found!")
            await state.clear()
            return
            
        session.delete(admin)
        session.commit()
        
    await message.answer("Admin successfully deleted!")
    await state.clear()

@router_admin.message(Command("edit_admin"))
@admin_only
async def edit_admin_start(message: types.Message, state: FSMContext):
    with Session() as session:
        admins = session.execute(select(Admin)).scalars().all()
    
    if not admins:
        await message.answer("No admins to edit!")
        return
        
    admin_list = []
    for admin in admins:
        admin_info = [f"ID: {admin.telegram_id}"]
        if admin.username:
            admin_info.append(f"@{admin.username}")
        admin_list.append(" - ".join(admin_info))
    
    await message.answer(
        "Current admins:\n" +
        "\n".join(admin_list) +
        "\n\nSend the Telegram ID of the admin you want to edit, or 'cancel' to abort."
    )
    await state.set_state(AdminManagement.edit_select_admin)

@router_admin.message(AdminManagement.edit_select_admin)
async def edit_admin_select_field(message: types.Message, state: FSMContext):
    if message.text.lower() == 'cancel':
        await message.answer("Operation cancelled.")
        await state.clear()
        return

    try:
        admin_id = int(message.text)
    except ValueError:
        await message.answer("Please send a valid Telegram ID or 'cancel'.")
        return

    with Session() as session:
        admin = session.execute(
            select(Admin).where(Admin.telegram_id == admin_id)
        ).scalar_one_or_none()
        
        if not admin:
            await message.answer("Admin not found!")
            await state.clear()
            return

    await state.update_data(admin_id=admin_id)
    await message.answer(
        "What field do you want to edit?\n"
        "- username\n"
        "- first_name\n"
        "- last_name\n"
        "\nOr send 'cancel' to abort."
    )
    await state.set_state(AdminManagement.edit_select_field)

@router_admin.message(AdminManagement.edit_select_field)
async def edit_admin_get_value(message: types.Message, state: FSMContext):
    field = message.text.lower()
    
    if field == 'cancel':
        await message.answer("Operation cancelled.")
        await state.clear()
        return
        
    if field not in ['username', 'first_name', 'last_name']:
        await message.answer("Please select a valid field or send 'cancel'.")
        return
        
    await state.update_data(field=field)
    await message.answer(f"Please send the new value for {field} (or 'none' to remove it):")
    await state.set_state(AdminManagement.edit_get_value)

@router_admin.message(AdminManagement.edit_get_value)
async def edit_admin_save(message: types.Message, state: FSMContext):
    data = await state.get_data()
    admin_id = data['admin_id']
    field = data['field']
    new_value = None if message.text.lower() == 'none' else message.text

    with Session() as session:
        admin = session.execute(
            select(Admin).where(Admin.telegram_id == admin_id)
        ).scalar_one_or_none()
        
        if not admin:
            await message.answer("Admin not found!")
            await state.clear()
            return
            
        setattr(admin, field, new_value)
        session.commit()

    await message.answer(f"Admin {field} successfully updated!")
    await state.clear()
        




