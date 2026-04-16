from utils.logger import get_logger

logger = get_logger(__name__)


class AssertionHelper:
    @staticmethod
    def _parse_json(response):
        try:
            return response.json()
        except Exception:
            raise ValueError(f"Response body is not valid JSON. Status: {response.status_code}, Body: {response.text[:200]}")

    @staticmethod
    def assert_status_code(response, expected):
        actual = response.status_code
        logger.debug(f"Asserting status code: expected={expected}, actual={actual}")
        assert actual == expected, f"Expected status {expected}, got {actual}. Body: {response.text}"

    def assert_key_in_response(self, response, key):
        body = self._parse_json(response)
        logger.debug(f"Asserting key '{key}' in response")
        assert key in body, f"Key '{key}' not found in response: {body}"

    @staticmethod
    def _get_nested(body, field):
        keys = field.split(".")
        value = body
        for key in keys:
            if not isinstance(value, dict):
                raise KeyError(f"Expected a dict at '{key}' but got {type(value).__name__}. Full path: '{field}'")
            if key not in value:
                raise KeyError(f"Key '{key}' not found in response. Full path: '{field}'")
            value = value[key]
        return value

    def assert_field_value(self, response, field, expected_value):
        body = self._parse_json(response)
        actual = self._get_nested(body, field)
        logger.debug(f"Asserting field '{field}': expected={expected_value}, actual={actual}")
        assert actual == expected_value, f"Field '{field}': expected '{expected_value}', got '{actual}'"

    def assert_schema(self, response, required_keys):
        body = self._parse_json(response)
        missing = [k for k in required_keys if k not in body]
        logger.debug(f"Asserting schema keys: {required_keys}")
        assert not missing, f"Missing keys in response: {missing}. Body: {body}"
