import logging
from aiogram import Bot, types
from aiogram.filters.command import Command
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table, func, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
import re

# Configure logging
logging.basicConfig(level=logging.INFO)

# SQLAlchemy setup
Base = declarative_base()
db_file = '../data/messages.db'

# Create the engine
engine = create_engine(f'sqlite:///{db_file}', 
                       connect_args={'check_same_thread': False}, 
                       pool_size=20,
                       max_overflow=0,
                       pool_timeout=30,
                       pool_recycle=1800)
Session = sessionmaker(bind=engine) 

user_category = Table('user_category', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

user_active_subscription = Table('user_active_subscription', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('subscription_id', Integer, ForeignKey('active_subscriptions.id'))
)

user_suspended_subscription = Table('user_suspended_subscription', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('sus_subscription_id', Integer, ForeignKey('suspended_subscriptions.id'))
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    chat_id = Column(Integer)
    referral_code = Column(String(10), unique=True)
    referred_by_id = Column(Integer, ForeignKey('users.id'))

    categories = relationship("Category", secondary=user_category, back_populates="users")
    active_subscriptions = relationship("ActiveSubscription", back_populates="user")
    suspended_subscriptions = relationship("SuspendedSubscription", back_populates="user")
    referral_data = relationship("ReferralData", uselist=False, back_populates="user")
    referred_by = relationship("User", remote_side=[id], back_populates="referrals")
    referrals = relationship("User", back_populates="referred_by")

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    keywords = Column(String, nullable=False)
    price_monthly = Column(Float, nullable=False)
    price_quarterly = Column(Float, nullable=False)
    price_yearly = Column(Float, nullable=False)
    users = relationship("User", secondary=user_category, back_populates="categories")
    active_subscriptions = relationship("ActiveSubscription", back_populates="category")
    suspended_subscriptions = relationship("SuspendedSubscription", back_populates="category")

class MessageRecord(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    chat_title = Column(String)
    message_link = Column(String)  # New field to replace message_id
    sender_id = Column(Integer, nullable=True)  # Made nullable for cases where sender might be unknown
    sender_name = Column(String)
    sender_username = Column(String, nullable=True)
    text = Column(String)
    date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    category_id = Column(Integer, ForeignKey('categories.id'))
    matched_keyword = Column(String)
    category = relationship("Category")

class ActiveSubscription(Base):
    __tablename__ = 'active_subscriptions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    subscription_type = Column(String, nullable=False)  # 'monthly', 'quarterly', or 'yearly'
   
    user = relationship("User", back_populates="active_subscriptions")
    category = relationship("Category", back_populates="active_subscriptions")

class SuspendedSubscription(Base):
    __tablename__ = 'suspended_subscriptions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    suspension_date = Column(DateTime, default=datetime.utcnow)
    original_end_date = Column(DateTime, nullable=False)
    subscription_type = Column(String, nullable=False)
    user = relationship("User", back_populates="suspended_subscriptions")
    category = relationship("Category", back_populates="suspended_subscriptions")

class ReferralData(Base):
    __tablename__ = 'referral_data'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    referral_balance = Column(Float, default=0.0)
    referrals_paid_count = Column(Integer, default=0)
    cash_income = Column(Float, default=0.0)
    activations_count = Column(Integer, default=0)
    people_paid_count = Column(Integer, default=0)
    payments_count = Column(Integer, default=0)
    payments_sum = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="referral_data")

# Create tables
Base.metadata.create_all(engine)

def message_matches_category(message_text, category):
    keywords = category.keywords.split(',')
    for keyword in keywords:
        keyword = keyword.strip().lower()
        if re.search(r'\b' + re.escape(keyword) + r'[\w]*\b', message_text.lower()):
            return keyword
    return None

async def cmd_start(message: types.Message):
    session = Session()
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
    session.close()
    return "Welcome! Use /subscribe to subscribe to categories."

async def cmd_subscribe(message: types.Message):
    print("lol")
    session = Session()
    categories = session.query(Category).all()
    category_list = "\n".join([f"{cat.id}: {cat.name}" for cat in categories])
    session.close()
    return f"Available categories:\n{category_list}\n\nUse /subscribe_to <category_id> to subscribe."


from sqlalchemy.orm import joinedload

async def cmd_subscribe_to(message: types.Message):
    try:
        category_id = int(message.text.split()[1])
    except (ValueError, IndexError):
        return "Invalid format. Use /subscribe_to <category_id>"

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
            session.flush()  

        category = session.query(Category).options(joinedload(Category.users)).filter(Category.id == category_id).first()
        if category:
            if user not in category.users:
                category.users.append(user)
                session.commit()
                return f"You've been subscribed to {category.name}."
            else:
                return f"You're already subscribed to {category.name}."
        else:
            return "Invalid category ID."
    except Exception as e:
        session.rollback()
        logging.error(f"Error in cmd_subscribe_to: {str(e)}")
        return "An error occurred while processing your request."
    finally:
        session.close()

async def add_category(message: types.Message):
    try:
        _, category_info = message.text.split(' ', 1)
        category_name, keywords = category_info.split(',', 1)
        
        session = Session()
        new_category = Category(name=category_name.strip(), keywords=keywords.strip())
        session.add(new_category)
        session.commit()
        session.close()
        
        return f"Category '{category_name.strip()}' added successfully."
    except ValueError:
        return "Invalid format. Use: /add_category Category Name, keyword1, keyword2, #hashtag1, #hashtag2"

async def start_scraping(bot: Bot, message: types.Message):
    await message.reply("Starting to scrape messages from all chats...")
    
    session = Session()
    categories = session.query(Category).all()
    
    chats = await bot.get_updates()
    print(chats)
    unique_chats = set()
    for update in chats:
        if update.message and update.message.chat not in unique_chats:
            unique_chats.add(update.message.chat)
    
    for chat in unique_chats:
        await message.reply(f"Scraping messages from {chat.title}...")
        
        async for msg in bot.get_chat_history(chat.id):
            for category in categories:
                matched_keyword = message_matches_category(msg.text or "", category)
                if matched_keyword:
                    new_message = MessageRecord(
                        chat_id=chat.id,
                        chat_title=chat.title,
                        message_id=msg.message_id,
                        sender_id=msg.from_user.id if msg.from_user else None,
                        sender_name=msg.from_user.full_name if msg.from_user else None,
                        sender_username=msg.from_user.username,
                        text=msg.text or "",
                        date=msg.date,
                        category_id=category.id,
                        matched_keyword=matched_keyword
                    )
                    session.add(new_message)
                print(msg.from_user.username)
                
    
    session.commit()
    session.close()
    
    await message.reply("Finished scraping messages.")
    await distribute_messages(bot)

async def distribute_messages(bot: Bot):
    session = Session()
    cutoff_time = datetime.utcnow() - timedelta(days=1)
    recent_messages = session.query(MessageRecord).filter(MessageRecord.created_at >= cutoff_time).all()

    for message in recent_messages:
        category = message.category
        subscribed_users = category.users
        for user in subscribed_users:
            try:
                await bot.send_message(
                    chat_id=user.chat_id,
                    text=f"New message in category '{category.name}':\n\n{message.text}\n\nFrom: {message.sender_name}, @{message.sender_username}\nChat: {message.chat_title}"
                )
            except Exception as e:
                logging.error(f"Failed to send message to user {user.id}: {e}")

    session.close()

async def get_stats(message: types.Message):
    session = Session()
    total_messages = session.query(MessageRecord).count()
    category_counts = session.query(Category.name, func.count(MessageRecord.id)).join(MessageRecord).group_by(Category.name).all()
    session.close()

    stats = f"Total messages scraped: {total_messages}\n\nMessages per category:\n"
    for category, count in category_counts:
        stats += f"{category}: {count}\n"

    return stats