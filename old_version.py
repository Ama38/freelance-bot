# @router_categories.callback_query(lambda c: c.data.startswith("category_"))
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
        

#         builder = InlineKeyboardBuilder()

#         builder.button(
#             text=f"Ежемесячная подписка: {category.price_monthly} руб/мес",
#             callback_data=f"price_{category.id}_1"
#         )

#         # Quarterly subscription button
#         builder.button(
#             text=f"Квартальная подписка: {category.price_quarterly} руб/3 мес",
#             callback_data=f"price_{category.id}_3"
#         )

#         # Yearly subscription button
#         builder.button(
#             text=f"Годовая подписка: {category.price_yearly} руб/год",
#             callback_data=f"price_{category.id}_12"
#         )

#         builder.button(text="Cancel", callback_data="cancel")
        

#         builder.adjust(1)

#         markup = InlineKeyboardBuilder()


#         await callback_query.message.answer(text="Выберите длительноость подписки:", reply_markup=builder.as_markup())
        


        

#     finally:
#         session.close()


#     await callback_query.answer()




# @router_categories.callback_query(F.data.startswith("price_"))
# async def process_subscription_selection(callback_query: CallbackQuery):
#     _, category_id, months = callback_query.data.split('_')
#     category_id = int(category_id)
#     months = int(months)

#     session = Session()
#     try:
#         user = session.query(User).filter(User.chat_id == callback_query.from_user.id).first()
#         if not user:
#             await callback_query.answer("User not found. Please start the bot first.")
#             return

#         category = session.query(Category).filter(Category.id == category_id).first()
#         if not category:
#             await callback_query.answer("Invalid category.")
#             return

#         # Check if user already has an active subscription for this category
#         existing_subscription = session.query(ActiveSubscription).filter(
#             ActiveSubscription.user_id == user.id,
#             ActiveSubscription.category_id == category.id,
#             ActiveSubscription.end_date > datetime.utcnow()
#         ).first()

#         if existing_subscription:
#             await callback_query.answer("You already have an active subscription for this category.")
#             return

#         # Calculate subscription details
#         start_date = datetime.utcnow()
#         end_date = start_date + timedelta(days=30 * months)
        
#         if months == 1:
#             price = category.price_monthly
#             subscription_type = "monthly"
#         elif months == 3:
#             price = category.price_quarterly
#             subscription_type = "quarterly"
#         elif months == 12:
#             price = category.price_yearly
#             subscription_type = "yearly"
#         else:
#             await callback_query.answer("Invalid subscription period.")
#             return

#         # Create new active subscription
#         new_subscription = ActiveSubscription(
#             user_id=user.id,
#             category_id=category.id,
#             start_date=start_date,
#             end_date=end_date,
#             subscription_type=subscription_type
#         )
#         session.add(new_subscription)

#         # Add user to category's users if not already there
#         if user not in category.users:
#             category.users.append(user)

#         session.commit()

#         await callback_query.message.answer(text=f"Subscription activated!\n"
#             f"Category: {category.name}\n"
#             f"Duration: {months} month(s)\n"
#             f"Price: {price} руб\n"
#             f"Valid until: {end_date.strftime('%Y-%m-%d')}", reply_markup=keyboard)

#     except Exception as e:
#         await callback_query.answer(f"An error occurred: {str(e)}")
#         session.rollback()
#     finally:
#         session.close()

#     await callback_query.answer()









# async def process_message(message_data: dict):
#     try:
#         session = Session()
#         categories = session.query(Category).all()
#         matched_categories = []
#         for category in categories:
#             matched_keyword = message_matches_category(message_data['text'] or "", category)
#             if matched_keyword:
#                 new_message = MessageRecord(
#                     chat_id=message_data['chat_id'],
#                     chat_title=message_data['chat_title'],
#                     message_link=message_data['message_link'],  # Using message_link instead of message_id
#                     sender_id=message_data['sender_id'],
#                     sender_name=message_data['sender_name'],
#                     sender_username=message_data['sender_username'],
#                     text=message_data['text'] or "",
#                     date=message_data['date'],
#                     category_id=category.id,
#                     matched_keyword=matched_keyword
#                 )
#                 session.add(new_message)
#                 matched_categories.append(category)
       
#         if matched_categories:
#             session.commit()
#             await distribute_message(message_data, matched_categories)
#     except Exception as e:
#         logging.error(f"Error in process_message: {str(e)}")
#         session.rollback()
#     finally:
#         session.close()