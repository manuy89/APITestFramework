import pytest


class TestUsers:
    def test_get_users(self, auth_client, assert_helper, config):
        response = auth_client.get(config["endpoints"]["users"]["base"], params={"page": 1})
        assert_helper.assert_status_code(response, 200)
        assert_helper.assert_schema(response, ["data", "page", "total"])

    @pytest.mark.parametrize("user_id", [1, 2, 3])
    def test_get_single_user(self, auth_client, user_repo, assert_helper, config, user_id):
        expected = user_repo.get_user(user_id)
        endpoint = config["endpoints"]["users"]["single"].format(id=user_id)
        response = auth_client.get(endpoint)
        assert_helper.assert_status_code(response, 200)
        data = response.json()["data"]
        assert data["email"] == expected["expected_email"]
        assert data["first_name"] == expected["expected_first_name"]

    def test_get_user_not_found(self, auth_client, assert_helper, config):
        endpoint = config["endpoints"]["users"]["single"].format(id=999)
        response = auth_client.get(endpoint)
        assert_helper.assert_status_code(response, 404)

    def test_create_user(self, auth_client, user_payloads, assert_helper, config):
        response = auth_client.post(config["endpoints"]["users"]["base"], json=user_payloads["create_user"])
        assert_helper.assert_status_code(response, 201)
        assert_helper.assert_schema(response, ["name", "job", "id", "createdAt"])
        assert_helper.assert_field_value(response, "name", user_payloads["create_user"]["name"])

    def test_update_user(self, auth_client, user_payloads, assert_helper, config):
        endpoint = config["endpoints"]["users"]["single"].format(id=2)
        response = auth_client.put(endpoint, json=user_payloads["update_user"])
        assert_helper.assert_status_code(response, 200)
        assert_helper.assert_field_value(response, "name", user_payloads["update_user"]["name"])

    def test_patch_user(self, auth_client, user_payloads, assert_helper, config):
        endpoint = config["endpoints"]["users"]["single"].format(id=2)
        response = auth_client.patch(endpoint, json=user_payloads["patch_user"])
        assert_helper.assert_status_code(response, 200)
        assert_helper.assert_field_value(response, "job", user_payloads["patch_user"]["job"])

    def test_delete_user(self, auth_client, assert_helper, config):
        endpoint = config["endpoints"]["users"]["single"].format(id=2)
        response = auth_client.delete(endpoint)
        assert_helper.assert_status_code(response, 204)
