#!/usr/bin/env python3
"""
Management script for Telegram bot operations.
"""

import sys
import argparse
from config import Config
from src.db.mssql import Database
from src.repository import MemberRepository
from src.services import MemberService
from src.workers.telegram import TelegramWorker
from logs.logger import LOGGER as logger

def kick_non_members():
    """Manually trigger the kick non-members task"""
    config = Config()
    config.load_from_env()
    
    db = Database(config)
    db.connect()
    
    try:
        # Initialize repository and services
        member_repo = MemberRepository(db)
        member_service = MemberService(member_repo)
        
        # Initialize worker and run kick task
        telegram_worker = TelegramWorker(config, member_service)
        telegram_worker.run_kick_task()
        
        print("Kick task completed successfully!")
        
    except Exception as e:
        print(f"Error running kick task: {e}")
        logger.error(f"Error in manual kick task: {e}")
    finally:
        if db:
            db.close()

def main():
    parser = argparse.ArgumentParser(description='Telegram Bot Management Commands')
    parser.add_argument('command', choices=['kick'], help='Command to run')
    
    args = parser.parse_args()
    
    if args.command == 'kick':
        kick_non_members()
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
