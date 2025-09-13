from src.repository import MemberRepository
from src.models.member import Member
from logs.logger import LOGGER as logger
from datetime import datetime
import asyncio

class MemberService:
    def __init__(self, repository: MemberRepository):
        self.repo: MemberRepository = repository

    def kick_non_member(self) -> None:
        # Get all non-members
        offset = 0
        while True:
            non_members = self.repo.get_non_members(limit=20, offset=offset)
            if not non_members:
                break
            for member in non_members:
                logger.info(f"Kicking non-member: {member.FirstName} {member.LastName} (ID: {member.Id})")
                # Here you would add the logic to kick the member from the Telegram group
                # For example, using Telegram Bot API to remove the user
                # bot.kick_chat_member(chat_id=GROUP_CHAT_ID, user_id=member.Id)
            logger.info(f"Kicked {len(non_members)} non-members.")
            offset += 20

    def get_member_by_phone(self, phone: str):
        phone = phone.replace(" ", "").replace("+", "").replace("-", "")
        if phone.startswith("62"):
            phone = "0" + phone[2:]
        return self.repo.get_by_phone(phone)
    
    def get_member_by_membership_time_batch(self, membership_time: str, limit: int = 20, offset: int = 0):
        return self.repo.get_member_by_membership_time(membership_time, limit, offset)
    
    def update_member(self, member: Member) -> None:
        self.repo.update_member(member)

    def get_member_by_user_telegram_id(self, telegram_id: int):
        return self.repo.get_member_by_telegram_id(telegram_id)
    
    async def kick_non_members(self):
        """Kick non-members from the Telegram group"""
        logger.info("Starting daily kick non-members task...")
        
        try:
            # Get all non-members from database
            offset = 0
            total_kicked = 0
            # 2025-10-31 00:00:00.000
            membership_end_time = datetime.now().strftime("%Y-%m-%d 00:00:00.000")
            while True:
                non_members = self.member_service.get_member_by_membership_time_batch(membership_end_time, limit=20, offset=offset)
                if not non_members:
                    break
                
                for member in non_members:
                    print(f"Processing non-member: {member.FirstName} {member.LastName} (ID: {member.Id}, Telegram ID: {member.UserTelegramId})")
                    try:
                        # Try to kick the user from the group
                        await self.bot.ban_chat_member(
                            chat_id=self.group_id,
                            user_id=member.UserTelegramId,
                            revoke_messages=False  # Don't delete their previous messages
                        )
                        
                        # Immediately unban them so they can rejoin if they become members
                        await self.bot.unban_chat_member(
                            chat_id=self.group_id,
                            user_id=member.UserTelegramId,
                            only_if_banned=True
                        )

                        member.UserTelegramId = None
                        member.HasJoinedTelegramGroup = False
                        await asyncio.to_thread(self.member_service.update_member, member)
                        
                        logger.info(f"Successfully kicked non-member: {member.FirstName} {member.LastName} (ID: {member.Id})")
                        total_kicked += 1
                        
                        # Add a small delay to avoid hitting rate limits
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        logger.error(f"Failed to kick user {member.Id}: {e}")
                    
                    except Exception as e:
                        logger.error(f"Unexpected error kicking user {member.Id}: {e}")
                
                offset += 20
                
                # Add delay between batches
                await asyncio.sleep(2)
            
            logger.info(f"Daily kick task completed. Total kicked: {total_kicked} non-members.")
            
        except Exception as e:
            logger.error(f"Error in kick_non_members task: {e}")
            import traceback
            logger.error(traceback.format_exc())