from logs import LOGGER as log
from config import Config
from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

class Database:
    ''' Database class to handle database connections '''
    def __init__(self, config: Config):
        encoded_password = quote_plus(config.database_password)
        self.conn_str = f"mssql+pyodbc://{config.database_user}:{encoded_password}@{config.database_host}/{config.database_name}?driver=ODBC+Driver+17+for+SQL+Server"
        self.conn = None
        self.__engine = None
        self.session = None
        self.debug = config.environment == "development"

    def connect(self):
        """Open a new database connection."""
        if self.__engine is None or self.session is None:
            self.__engine = create_engine(
                self.conn_str, 
                pool_size=10,          # keep 10 connections in pool
                max_overflow=20,       # allow 20 extra if needed (total 30)
                pool_timeout=30,       # wait max 30s before giving up on getting a connection
                pool_recycle=1800,     # recycle connections after 30 mins (avoid stale connections)
                pool_pre_ping=True,    # check if connection is alive before using it
                echo=self.debug             # set to True for SQL debug logs
            )
            Session = sessionmaker(bind=self.__engine)
            self.session = Session()

        self.ping()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

        log.info("Database connection closed")
    
    def ping(self) -> bool:
        """Check if the DB connection is alive (without reconnecting)."""
        try:
            self.session.execute(text("SELECT 1"))
            log.info("Database connection is alive")
            return True
        except Exception as e:
            log.error(f"Database connection is not alive: {e}")
            return False