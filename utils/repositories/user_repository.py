from utils.db_client import DBClient


class UserRepository:
    def __init__(self, db: DBClient):
        self.db = db

    def get_user(self, user_id: int):
        return self.db.fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))

    def get_all_users(self):
        return self.db.fetch_all("SELECT * FROM users")
