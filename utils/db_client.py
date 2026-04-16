import sqlite3
from config.paths import DB_PATH
from utils.logger import get_logger

logger = get_logger(__name__)


class DBClient:
    def __init__(self):
        if not DB_PATH.exists():
            raise FileNotFoundError(f"Database not found at {DB_PATH}. Run test_data/setup_db.py first.")
        try:
            self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            logger.debug(f"Connected to database: {DB_PATH}")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def fetch_all(self, query, params=()):
        try:
            results = self.conn.execute(query, params).fetchall()
            if not results:
                logger.warning(f"No records found | query={query} | params={params}")
                return []
            return results
        except sqlite3.Error as e:
            logger.error(f"fetch_all failed | query={query} | error={e}")
            raise

    def fetch_one(self, query, params=()):
        try:
            result = self.conn.execute(query, params).fetchone()
            if result is None:
                logger.warning(f"No record found | query={query} | params={params}")
            return result
        except sqlite3.Error as e:
            logger.error(f"fetch_one failed | query={query} | error={e}")
            raise

    def close(self):
        try:
            self.conn.close()
            logger.debug("Database connection closed")
        except sqlite3.Error as e:
            logger.error(f"Error closing database connection: {e}")
            raise
