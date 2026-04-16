from pathlib import Path

# root of the project
ROOT = Path(__file__).resolve().parent.parent

# config
CONFIG_PATH = ROOT / "config" / "config.json"
ENVIRONMENTS_DIR = ROOT / "config" / "environments"

# test data
TEST_DATA_DIR = ROOT / "test_data"
PAYLOADS_DIR = TEST_DATA_DIR / "payloads"
DB_PATH = TEST_DATA_DIR / "test_db.sqlite"

# payloads
AUTH_PAYLOAD = PAYLOADS_DIR / "auth.json"
USERS_PAYLOAD = PAYLOADS_DIR / "users.json"

# logs
LOGS_DIR = ROOT / "logs"
LOG_FILE = LOGS_DIR / "test_run.log"
