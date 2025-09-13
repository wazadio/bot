import schedule
import time
import threading
from datetime import datetime
from logs.logger import LOGGER as logger
from src.workers.telegram import TelegramWorker
import os

class Scheduler:
    def __init__(self, telegram_worker: TelegramWorker):
        self.telegram_worker = telegram_worker
        self.is_running = False
        self.scheduler_thread = None

    def setup_schedule(self):
        """Setup the daily schedule for kicking non-members"""
        # Schedule the task to run every day at 9:00 AM
        schedule.every().day.at(os.getenv("TELEGRAM_CLEANING_SCHEDULE", "00:01")).do(self._run_kick_task)
        
        # You can also add other schedules:
        # schedule.every().hour.do(self._run_kick_task)  # Run every hour
        # schedule.every().monday.at("10:00").do(self._run_kick_task)  # Run every Monday at 10 AM
        
        logger.info(f"Scheduled daily kick task at {kick_time}")

    def _run_kick_task(self):
        """Internal method to run the kick task with logging"""
        logger.info(f"Running scheduled kick task at {datetime.now()}")
        try:
            self.telegram_worker.run_kick_task()
            logger.info("Scheduled kick task completed successfully")
        except Exception as e:
            logger.error(f"Error in scheduled kick task: {e}")

    def start(self):
        """Start the scheduler in a separate thread"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.setup_schedule()
        self.is_running = True
        
        def run_scheduler():
            logger.info("Scheduler started")
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            logger.info("Scheduler stopped")
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Scheduler thread started")

    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            return
        
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        logger.info("Scheduler stopped")

    def run_now(self):
        """Manually trigger the kick task immediately"""
        logger.info("Manually triggering kick task")
        self._run_kick_task()

    def get_next_run_time(self):
        """Get the next scheduled run time"""
        jobs = schedule.jobs
        if jobs:
            return min(job.next_run for job in jobs)
        return None
    
    def payment_reminder(self):
        """Send payment reminders to users"""
        logger.info("Sending payment reminders")
        # Implement the logic to send payment reminders
        pass
