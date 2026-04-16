from utils.db_client import DBClient


class AuthRepository:
    def __init__(self, db: DBClient):
        self.db = db

    def get_scenario(self, scenario: str):
        return self.db.fetch_one("SELECT * FROM auth WHERE scenario = ?", (scenario,))

    def get_all_scenarios(self):
        return self.db.fetch_all("SELECT * FROM auth")
