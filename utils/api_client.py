import requests
from requests.exceptions import Timeout, ConnectionError, RequestException
from utils.logger import get_logger

logger = get_logger(__name__)


class APIClient:
    def __init__(self, base_url, timeout=10, api_key=None):
        if not base_url:
            raise ValueError("base_url is required to initialize APIClient")
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"x-api-key": api_key})

    def set_auth(self, token):
        if not token:
            raise ValueError("Auth token is None or empty — login may have failed")
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def _request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            logger.info(f"{method} {url} -> {response.status_code}")
            truncated_body = response.text[:200] + "..." if len(response.text) > 200 else response.text
            logger.debug(f"Response body: {truncated_body}")
            return response
        except Timeout:
            logger.error(f"{method} {url} timed out after {self.timeout}s")
            raise
        except ConnectionError:
            logger.error(f"{method} {url} failed — connection error")
            raise
        except RequestException as e:
            logger.error(f"{method} {url} failed — {e}")
            raise

    def get(self, endpoint, **kwargs):
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self._request("PUT", endpoint, **kwargs)

    def patch(self, endpoint, **kwargs):
        return self._request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self._request("DELETE", endpoint, **kwargs)
