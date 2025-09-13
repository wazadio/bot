from config import Config
from src.db.mssql import Database
from src.repository import MemberRepository
from src.services import MemberService
from src.handlers import TelegramBotHandler
from src.workers.telegram import TelegramWorker
from src.workers.scheduler import Scheduler
from logs.logger import LOGGER as logger

def main():
    config = Config()
    config.load_from_env()
    
    db = Database(config)
    db.connect()

    # Initialize repository 
    member_repo = MemberRepository(db)

    # Initialize services
    member_service = MemberService(config, member_repo)

    # Initialize Telegram bot and worker
    telegram_bot = TelegramBotHandler(config, member_service)
    telegram_worker = TelegramWorker(config, member_service)
    
    # Initialize scheduler
    scheduler = Scheduler(telegram_worker)
    
    logger.info("Starting application...")
    
    try:
        # Start the scheduler
        scheduler.start()
        logger.info("Scheduler started successfully")
        
        # Log next scheduled run
        next_run = scheduler.get_next_run_time()
        if next_run:
            logger.info(f"Next kick task scheduled for: {next_run}")
        
        # Run the bot using synchronous approach
        logger.info("Starting Telegram bot...")
        telegram_bot.run()
    except KeyboardInterrupt:
        print("\nShutdown requested...")
        logger.info("Shutdown requested by user")
    except Exception as e:
        print(f"Error in main: {e}")
        logger.error(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Stop scheduler
        logger.info("Stopping scheduler...")
        scheduler.stop()
        
        # Close database connection
        if db:
            db.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutdown complete.")