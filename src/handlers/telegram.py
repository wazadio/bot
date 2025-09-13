from config import Config
from src.services import MemberService
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from logs.logger import LOGGER as logger
import asyncio
from datetime import datetime, timedelta
import datetime as dt
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ChatJoinRequestHandler, ChatMemberHandler
from src.utils import extract_phone_number

class TelegramBotHandler:
    def __init__(self, config: Config, member_service: MemberService):
        self.token = config.telegram_bot_token
        self.group_id = config.telegram_group_id
        self.member_service = member_service

    def run(self):
        """Start the Telegram bot."""
        logger.info(f"Initializing bot with token: {self.token[:10]}...")
        
        app = ApplicationBuilder().token(self.token).build()

        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(MessageHandler(filters.CONTACT, self.handle_contact))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        # app.add_handler(ChatJoinRequestHandler(callback=self.approve_join_request))
        # app.add_handler(ChatMemberHandler(self.track_chat_member_updates, ChatMemberHandler.CHAT_MEMBER))

        logger.info("Starting Telegram bot...")
        try:
            logger.info("Starting polling...")
            app.run_polling(
                drop_pending_updates=True,
                timeout=30,
                read_timeout=30,
                write_timeout=30,
                connect_timeout=30
            )
        except KeyboardInterrupt:
            logger.info("Bot stopped by user (Ctrl+C)")
        except Exception as e:
            logger.error(f"Error running bot: {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            logger.info("Bot shutdown complete")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [[KeyboardButton("Share my phone number", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            "Hi! Please share your phone number to join the group.",
            reply_markup=reply_markup
        )

    async def handle_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        contact = update.message.contact
        phone_number = contact.phone_number.replace(" ", "")
        user_id = update.message.from_user.id

        logger.info(f"Received contact from user {user_id} with phone {phone_number}")

        # Run synchronous DB call in thread to avoid blocking
        member = await asyncio.to_thread(self.member_service.get_member_by_phone, phone_number)

        if member:
            try:
                if not member.HasJoinedTelegramGroup and member.MembershipTime >= datetime.now():
                    # Create a link that expires in 1 hour and requires approval
                    expired_at = datetime.now() + timedelta(hours=1)

                    invite_link = await context.bot.create_chat_invite_link(
                        chat_id=self.group_id,
                        member_limit=1,        # one-time use
                        expire_date=None  # expires in 1 hour
                    )

                    print("expired_at:", expired_at)
                    print(f"Invite link created for user {user_id}: {invite_link.invite_link}, expires at {expired_at}")
                    
                    member.UserTelegramId = user_id
                    member.HasJoinedTelegramGroup = True
                    await asyncio.to_thread(self.member_service.update_member, member)

                    await update.message.reply_text(
                        f"✅ Approved! Here’s your one-time group link:\n{invite_link.invite_link}\n\nThis link will expire in 1 hour or after one use."
                    )
                    logger.info(f"Sent invite link to user {user_id}, link: {invite_link.invite_link}")
                elif member.HasJoinedTelegramGroup:
                    await update.message.reply_text("ℹ️ Link already sent, or you have already joined the group.")
                    logger.info(f"User {user_id} has already joined the group")
                elif member.MembershipTime < datetime.now():
                    await update.message.reply_text("❌ Your membership has expired. Please renew to join the group.")
                    logger.info(f"User {user_id} has expired membership")
            except Exception as e:
                await update.message.reply_text("❌ Failed to create invite link. Please contact admin.")
                logger.error(f"Error creating invite link for user {user_id}: {e}")
        else:
            await update.message.reply_text("❌ You are not registered. Cannot add to the group.")
            logger.warning(f"User {user_id} with phone {phone_number} is not registered")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages, including phone numbers"""
        message_text = update.message.text.strip()
        user_id = update.message.from_user.id
        
        logger.info(f"Received message from user {user_id}: {message_text}")
        
        # Check if the message looks like a phone number
        phone_number = extract_phone_number(message_text)
        
        if phone_number:
            logger.info(f"Extracted phone number {phone_number} from user {user_id}")
            
            # Run synchronous DB call in thread to avoid blocking
            member = await asyncio.to_thread(self.member_service.get_member_by_phone, phone_number)
            
            if member:
                try:
                    if not member.HasJoinedTelegramGroup and member.MembershipTime >= datetime.now():
                        # Create a link that expires in 1 hour and requires approval
                        expired_at = datetime.now() + timedelta(hours=1)

                        invite_link = await context.bot.create_chat_invite_link(
                            chat_id=self.group_id,
                            member_limit=1,        # one-time use
                            expire_date=None  # expires in 1 hour
                        )

                        print("expired_at:", expired_at)
                        print(f"Invite link created for user {user_id}: {invite_link.invite_link}, expires at {expired_at}")
                        
                        member.UserTelegramId = user_id
                        member.HasJoinedTelegramGroup = True
                        await asyncio.to_thread(self.member_service.update_member, member)

                        await update.message.reply_text(
                            f"✅ Approved! Here's your one-time group link:\n{invite_link.invite_link}\n\nThis link will expire in 1 hour or after one use."
                        )
                        logger.info(f"Sent invite link to user {user_id}, link: {invite_link.invite_link}")
                    elif member.HasJoinedTelegramGroup:
                        await update.message.reply_text("ℹ️ Link already sent, or you have already joined the group.")
                        logger.info(f"User {user_id} has already joined the group")
                    elif member.MembershipTime < datetime.now():
                        await update.message.reply_text("❌ Your membership has expired. Please renew to join the group.")
                        logger.info(f"User {user_id} has expired membership")
                except Exception as e:
                    await update.message.reply_text("❌ Failed to create invite link. Please contact admin.")
                    logger.error(f"Error creating invite link for user {user_id}: {e}")
            else:
                await update.message.reply_text("❌ Phone number not found in our records. Please make sure you're using the correct phone number.")
                logger.warning(f"User {user_id} with phone {phone_number} is not registered")
        else:
            # Not a phone number, provide help
            await update.message.reply_text(
                "Please send your phone number in one of these formats:\n"
                "• +628123456789\n"
                "• 08123456789\n"
                "• 628123456789\n\n"
                "Or use the 'Share my phone number' button by typing /start"
            )


    async def approve_join_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle join requests to the group"""
        logger.info("approve_join_request handler triggered!")
        
        if not update.chat_join_request:
            logger.warning("No chat_join_request found in update")
            return
            
        join_request = update.chat_join_request
        user = join_request.from_user
        user_id = user.id

        logger.info(f"Received join request from user {user_id} ({user.first_name})")

        try:
            # check your member service (runs in thread pool)
            member = await asyncio.to_thread(
                self.member_service.get_member_by_user_telegram_id,
                user_id
            )

            if not member or member.HasJoinedTelegramGroup:
                logger.warning(f"User {user_id} is not a registered member, declining join request")
                await context.bot.decline_chat_join_request(
                    chat_id=self.group_id,
                    user_id=user_id
                )
                return
            
            # Check if membership is still valid
            if member.MembershipTime < datetime.now():
                logger.warning(f"User {user_id} has expired membership, declining join request")
                await context.bot.decline_chat_join_request(
                    chat_id=self.group_id,
                    user_id=user_id
                )
                return
            
            # approve request
            await context.bot.approve_chat_join_request(
                chat_id=self.group_id,
                user_id=user_id
            )
            
            # Update member status
            member.HasJoinedTelegramGroup = True
            await asyncio.to_thread(self.member_service.update_member, member)
            
            logger.info(f"Approved join request for user {user_id}")

        except Exception as e:
            logger.error(f"Error approving join request for user {user_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())

    async def track_chat_member_updates(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Track when users join or leave the group"""
        try:
            chat_member_update = update.chat_member
            if not chat_member_update:
                return
                
            user = chat_member_update.from_user
            new_status = chat_member_update.new_chat_member.status
            old_status = chat_member_update.old_chat_member.status
            
            # Check if user joined the group
            if old_status in ['left', 'kicked'] and new_status in ['member', 'administrator', 'creator']:
                logger.info(f"User {user.id} ({user.first_name}) joined the group")
                
                # Update member status in database
                member = await asyncio.to_thread(
                    self.member_service.get_member_by_user_telegram_id,
                    user.id
                )
                
                if member:
                    member.HasJoinedTelegramGroup = True
                    await asyncio.to_thread(self.member_service.update_member, member)
                    logger.info(f"Updated HasJoinedTelegramGroup for user {user.id}")
                    
            # Check if user left the group
            elif old_status in ['member', 'administrator'] and new_status in ['left', 'kicked']:
                logger.info(f"User {user.id} ({user.first_name}) left the group")
                
                # Update member status in database
                member = await asyncio.to_thread(
                    self.member_service.get_member_by_user_telegram_id,
                    user.id
                )
                
                if member:
                    member.HasJoinedTelegramGroup = False
                    await asyncio.to_thread(self.member_service.update_member, member)
                    logger.info(f"Updated HasJoinedTelegramGroup for user {user.id}")
                    
        except Exception as e:
            logger.error(f"Error in track_chat_member_updates: {e}")