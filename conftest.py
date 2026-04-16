import pytest
import json
import os
from dotenv import load_dotenv
from config.paths import ENVIRONMENTS_DIR, AUTH_PAYLOAD, USERS_PAYLOAD, DB_PATH, CONFIG_PATH, LOGS_DIR
from utils.api_client import APIClient
from utils.db_client import DBClient
from utils.logger import get_logger, stop_listener
from utils.assertions import AssertionHelper
from utils.repositories.auth_repository import AuthRepository
from utils.repositories.user_repository import UserRepository
from test_data.setup_db import setup as setup_database

load_dotenv()


def pytest_runtest_setup(item):
    logger = get_logger("test_runner")
    logger.info(f"{'='*60}")
    logger.info(f"TEST START: {item.nodeid}")
    logger.info(f"{'='*60}")


def pytest_runtest_logreport(report):
    if report.when == "call":
        logger = get_logger("test_runner")
        status = "PASSED" if report.passed else "FAILED" if report.failed else "SKIPPED"
        logger.info(f"{'-'*60}")
        logger.info(f"TEST END: {report.nodeid} | STATUS: {status}")
        logger.info(f"{'='*60}\n")


def pytest_sessionfinish(session, exitstatus):
    worker = os.getenv("PYTEST_XDIST_WORKER")
    if worker:
        return

    worker_logs = sorted(LOGS_DIR.glob("test_run_gw*.log"))
    if not worker_logs:
        return

    merged_log = LOGS_DIR / "test_run.log"
    with merged_log.open("w") as outfile:
        for log_file in worker_logs:
            outfile.write(f"{'#'*60}\n")
            outfile.write(f"# WORKER: {log_file.stem}\n")
            outfile.write(f"{'#'*60}\n")
            outfile.write(log_file.read_text())
            outfile.write("\n")

    master_log = LOGS_DIR / "test_run_master.log"
    if master_log.exists():
        master_log.unlink()

def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="dev", help="Environment to run tests against: dev, staging, prod")
    parser.addoption("--reset-db", action="store_true", default=False, help="Force reset the test database")


@pytest.fixture(scope="session")
def config(pytestconfig):
    env = pytestconfig.getoption("--env")

    # load shared config
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Shared config not found: {CONFIG_PATH}")
    try:
        cfg = json.loads(CONFIG_PATH.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file {CONFIG_PATH}: {e}")

    # load and merge environment config
    env_config_path = ENVIRONMENTS_DIR / f"{env}.json"
    if not env_config_path.exists():
        raise FileNotFoundError(f"Environment config not found: {env_config_path}. Valid envs: dev, staging, prod")
    try:
        env_cfg = json.loads(env_config_path.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in environment config {env_config_path}: {e}")

    cfg.update(env_cfg)

    # load sensitive values from .env
    api_key = os.getenv("API_KEY")
    email = os.getenv("API_EMAIL")
    password = os.getenv("API_PASSWORD")

    missing_env = [k for k, v in {"API_KEY": api_key, "API_EMAIL": email, "API_PASSWORD": password}.items() if not v]
    if missing_env:
        raise EnvironmentError(f"Missing required environment variables: {missing_env}. Check your .env file.")

    cfg["api_key"] = api_key
    cfg["credentials"] = {"email": email, "password": password}

    required_keys = ["base_url", "timeout", "api_key", "credentials", "endpoints"]
    missing = [k for k in required_keys if k not in cfg]
    if missing:
        raise KeyError(f"Missing required config keys: {missing}")

    return cfg


@pytest.fixture(scope="session", autouse=True)
def init_db(pytestconfig, worker_id):
    force_reset = pytestconfig.getoption("--reset-db")
    # only master worker sets up the DB to avoid race conditions
    if worker_id == "master" or worker_id == "gw0":
        if force_reset or not DB_PATH.exists():
            try:
                setup_database()
            except Exception as e:
                pytest.exit(f"Database setup failed: {e}")


@pytest.fixture(scope="session")
def worker_id(request):
    return os.getenv("PYTEST_XDIST_WORKER", "master")


@pytest.fixture(scope="session")
def client(config):
    return APIClient(base_url=config["base_url"], timeout=config["timeout"], api_key=config["api_key"])


@pytest.fixture(scope="session")
def auth_client(client, config):
    creds = config["credentials"]
    login_endpoint = config["endpoints"]["auth"]["login"]
    response = client.post(login_endpoint, json=creds)
    if response.status_code != 200:
        pytest.exit(f"Login failed with status {response.status_code}: {response.text}")
    token = response.json().get("token")
    client.set_auth(token)
    return client


@pytest.fixture(scope="session")
def auth_payloads():
    if not AUTH_PAYLOAD.exists():
        raise FileNotFoundError(f"Payload file not found: {AUTH_PAYLOAD}")
    return json.loads(AUTH_PAYLOAD.read_text())


@pytest.fixture(scope="session")
def user_payloads():
    if not USERS_PAYLOAD.exists():
        raise FileNotFoundError(f"Payload file not found: {USERS_PAYLOAD}")
    return json.loads(USERS_PAYLOAD.read_text())


@pytest.fixture(scope="session")
def db():
    db_client = DBClient()
    yield db_client
    db_client.close()


@pytest.fixture(scope="session")
def auth_repo(db):
    return AuthRepository(db)


@pytest.fixture(scope="session")
def user_repo(db):
    return UserRepository(db)


@pytest.fixture(scope="session", autouse=True)
def shutdown_logger():
    yield
    stop_listener()


@pytest.fixture(scope="session")
def assert_helper():
    return AssertionHelper()
