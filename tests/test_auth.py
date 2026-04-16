class TestAuth:
    def test_login_success(self, client, auth_payloads, auth_repo, assert_helper, config):
        scenario = auth_repo.get_scenario("valid_login")
        response = client.post(config["endpoints"]["auth"]["login"], json=auth_payloads["valid_login"])
        assert_helper.assert_status_code(response, scenario["expected_status"])
        assert_helper.assert_key_in_response(response, "token")

    def test_login_missing_password(self, client, auth_payloads, auth_repo, assert_helper, config):
        scenario = auth_repo.get_scenario("missing_password")
        response = client.post(config["endpoints"]["auth"]["login"], json=auth_payloads["missing_password"])
        assert_helper.assert_status_code(response, scenario["expected_status"])
        assert_helper.assert_field_value(response, "error", scenario["expected_error"])

    def test_register_success(self, client, auth_payloads, auth_repo, assert_helper, config):
        scenario = auth_repo.get_scenario("valid_register")
        response = client.post(config["endpoints"]["auth"]["register"], json=auth_payloads["valid_register"])
        assert_helper.assert_status_code(response, scenario["expected_status"])
        assert_helper.assert_key_in_response(response, "token")

    def test_register_missing_password(self, client, auth_payloads, auth_repo, assert_helper, config):
        scenario = auth_repo.get_scenario("missing_password_register")
        response = client.post(config["endpoints"]["auth"]["register"], json=auth_payloads["missing_password_register"])
        assert_helper.assert_status_code(response, scenario["expected_status"])
        assert_helper.assert_field_value(response, "error", scenario["expected_error"])
