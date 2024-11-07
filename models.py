import logging
from aiogram import Bot, types
from aiogram.filters.command import Command
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table, func, Float, Boolean
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
    used_trials = relationship("UsedTrial", back_populates="user")

class UsedTrial(Base):
    __tablename__ = 'used_trials'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    used_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="used_trials")
    category = relationship("Category", back_populates="used_trials")
    
    




class Admin(Base):
    __tablename__ = "admins_table"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)

    def __repr__(self):
        return f"<TelegramAdmin(telegram_id={self.telegram_id}, username={self.username})>"


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    keywords = Column(String, nullable=False)
    has_3_days_free = Column(Boolean, nullable=False)
    price_monthly = Column(Float, nullable=False)
    price_quarterly = Column(Float, nullable=False)
    price_half_yearly = Column(Float, nullable=False)
    price_yearly = Column(Float, nullable=False)
    bot_token = Column(String)
    bot_username = Column(String)
    users = relationship("User", secondary=user_category, back_populates="categories")
    active_subscriptions = relationship("ActiveSubscription", back_populates="category", cascade="all, delete-orphan")
    suspended_subscriptions = relationship("SuspendedSubscription", back_populates="category")
    used_trials = relationship("UsedTrial", back_populates="category")


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