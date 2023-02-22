"""
E-Mail Validation Testing Routines
(C) 2023 Dierk-Bent Piening
E-Mail: dierk-bent.piening@mailbox.org
"""
import pytest
from emailkit.emailvalidator import EmailAddressValidator


class TestEmailValidation:
    def pytest_configure(config):
        plugin = config.pluginmanager.getplugin("mypy")
        plugin.mypy_argv.append("--check-untyped-defs")

    def test_validate_success(self):
        result_bool, result_dict = EmailAddressValidator().validate_email_address(
            "test@test.com"
        )
        assert result_bool is True, "SUCCESS BOOL"
        assert len(result_dict) == 0, "SUCCESS LEN(RESULT)"

    def test_address_part_check(self):
        result_bool, result_dict = EmailAddressValidator().validate_email_address(
            "test@test.test.com"
        )
        assert result_bool is False, "SUCCESS BOOL"
        assert len(result_dict) == 1, "SUCCESS LEN(RESULT)"

    def test_wrong_character_individual_address(self):
        result_bool, result_dict = EmailAddressValidator().validate_email_address(
            "te st@test.com"
        )
        assert result_bool is False, "SUCCESS BOOL"
        assert len(result_dict) == 1, "SUCCESS LEN(RESULT)"
        assert "individual_address" in result_dict, "CHECK IF KEY in Result dict"
        assert (
            result_dict["individual_address"][0]["type"] == "invalid_character"
        ), "Check if 'type': 'invalid_character' is in Result Dict "

    def test_wrong_character_domain(self):
        result_bool, result_dict = EmailAddressValidator().validate_email_address(
            "test@gmx.d e"
        )
        assert result_bool is False, "Check if address is correct marked as invalid"
        assert result_dict["toplevel_domain"][0]['type'] == "invalid_character"

    def test_min_length_domain_check(self):
        result_bool, result_dict = EmailAddressValidator().validate_email_address(
            "test@t.com"
        )
        assert result_bool is False, "Success if Bool = False"
        assert len(result_dict) == 1, "SUCCESS LEN(RESULT)"
        assert (
            "domain" in result_dict
        ), "test if domain issue is listed correct in result dict"
        assert (
            result_dict["domain"][0]["type"] == "min_length"
        ), "Test if issue in domain is listed as min_length"
        assert (
            result_dict["domain"][0]["exspected_length"] == 3
        ), "Test if length given by rule is listed correct in issue"
        assert (
            result_dict["domain"][0]["provided_length"] == 1
        ), "Test if provided length of domain is listed correct"

    def test_max_length_domain_check(self):
        validator = EmailAddressValidator()
        validator.domain_max_length = 5
        result_bool, result_dict = validator.validate_email_address("test@tttttt.com")
        assert result_bool is False, "Success if Bool = False"
        assert len(result_dict) == 1, "SUCCESS LEN(RESULT) = 1"
        assert (
            "domain" in result_dict
        ), "test if domain issue is listed correct in result dict"
        assert (
            result_dict["domain"][0]["type"] == "max_length"
        ), "Test if issue in domain is listed as min_length"
        assert (
            result_dict["domain"][0]["exspected_length"] == 5
        ), "Test if length given by rule is listed correct in issue"
        assert (
            result_dict["domain"][0]["provided_length"] == 6
        ), "Test if provided length of domain is listed correct"

    def test_aet_character_check(self):
        result_bool, result_dict = EmailAddressValidator().validate_email_address(
            "testtest.com"
        )
        assert result_bool is False, "Success if Bool = False"
        assert (
            "basic_pattern" in result_dict
        ), "Check if basic_pattern issue is in result dict"
