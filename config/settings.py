from dotenv import load_dotenv
import os

class Config:
    '''Application configuration settings.'''
    def __init__(self) -> None:
        self.telegram_bot_token: str = None
        self.telegram_bot_username: str = None
        self.database_host: str = None
        self.database_port: int = None
        self.database_name: str = None
        self.database_user: str = None
        self.database_password: str = None
        self.environment: str = None
        self.telegram_group_id: int = None

    def load_from_env(self) -> None:
        '''Load configuration from environment dictionary.'''
        load_dotenv()
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_bot_username = os.getenv("TELEGRAM_BOT_USERNAME")
        self.database_host = os.getenv("DATABASE_HOST")
        self.database_port = int(os.getenv("DATABASE_PORT"))
        self.database_name = os.getenv("DATABASE_NAME")
        self.database_user = os.getenv("DATABASE_USER")
        self.database_password = os.getenv("DATABASE_PASSWORD")
        self.environment = os.getenv("ENVIRONMENT")
        self.telegram_group_id = int(os.getenv("TELEGRAM_GROUP_ID"))