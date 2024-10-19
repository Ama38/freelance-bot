# async def catch_messages():
#     retry_count = 0
#     max_retries = 3
   
#     while retry_count < max_retries:
#         client = None
#         try:
#             client = TelegramClient(session_file, api_id, api_hash)
           
#             logger.info("Starting Telethon client...")
#             await client.start(phone=phone_number)

#             if not await client.is_user_authorized():
#                 logger.info("User is not authorized. Starting authentication process...")
#                 await client.send_code_request(phone_number)
#                 try:
#                     logger.info("Please check your phone for the authentication code.")
#                     code = input("Enter the code: ")
#                     await client.sign_in(phone_number, code)
#                 except SessionPasswordNeededError:
#                     password = input("Two-step verification is enabled. Please enter your password: ")
#                     await client.sign_in(password=password)

#             logger.info("Authentication successful!")
           
#             @client.on(events.NewMessage)
#             async def handle_new_message(event):
#                 try:
#                     await process_message(event)
#                 except Exception as e:
#                     logger.error(f"Error processing message: {e}")

#             logger.info("Telethon client is now running...")
#             await client.run_until_disconnected()
       
#         except AuthKeyUnregisteredError:
#             logger.error("Session expired. Will attempt to re-authenticate on next retry.")
#             retry_count += 1
#         except ConnectionError as e:
#             logger.error(f"Connection error: {e}. Retrying...")
#             retry_count += 1
#         except Exception as e:
#             logger.error(f"An unexpected error occurred: {e}")
#             retry_count += 1
#         finally:
#             if client:
#                 await client.disconnect()
       
#         if retry_count < max_retries:
#             wait_time = min(30, 10 * (retry_count + 1))  # Exponential backoff, max 30 seconds
#             logger.info(f"Retrying in {wait_time} seconds... (Attempt {retry_count + 1}/{max_retries})")
#             await asyncio.sleep(wait_time)
#         else:
#             logger.error("Max retries reached. Please check your account and try again later.")
#             break