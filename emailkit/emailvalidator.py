"""
E-Mail Validator
(C) 2023 Dierk-Bent Piening
E-Mail: dierk-bent.piening@mailbox.org
this if free software, you can modify or redistriute it under the terms of the general public license (GPL v2)

"""
from .exceptions import EmailAddressValidationException

class EmailAddressValidator:
    def __init__(
        self,
        addressparts=None,
        allowed_characters_email=None,
        allowed_characters_domain=None,
        max_length_domain: int = 69,
        min_length_domain: int = 3,
    ):
        if allowed_characters_email is None:
            self._allowed_characters_email: tuple[str, ...] = (
                "a",
                "b",
                "c",
                "d",
                "e",
                "f",
                "g",
                "h",
                "i",
                "j",
                "k",
                "l",
                "m",
                "n",
                "o",
                "p",
                "q",
                "r",
                "s",
                "t",
                "u",
                "v",
                "w",
                "x",
                "y",
                "z",
                "-",
                "_",
                "+",
                ".",
            )
        else:
            self._allowed_characters_email = allowed_characters_email
        if allowed_characters_domain is None:
            self._allowed_characters_domain: tuple[str, ...] = (
                "a",
                "b",
                "c",
                "d",
                "e",
                "f",
                "g",
                "h",
                "i",
                "j",
                "k",
                "l",
                "m",
                "n",
                "o",
                "p",
                "q",
                "r",
                "s",
                "t",
                "u",
                "v",
                "w",
                "x",
                "y",
                "z",
                "-",
            )
        else:
            self._allowed_characters_domain = allowed_characters_domain
        if addressparts is None:
            self._addressparts: tuple[str, ...] = (
                "individual_address",
                "domain",
                "toplevel_domain",
            )
        else:
            self._addressparts = addressparts
        self._max_length_domain: int = max_length_domain
        self._min_length_domain: int = min_length_domain
        self._use_exception: bool = False

    @property
    def use_exception(self) -> bool:
        return self._use_exception

    @use_exception.setter
    def use_exception(self, use_exception: bool) -> None:
        self._use_exception = use_exception

    @property
    def domain_min_length(self):
        return self._min_length_domain

    @domain_min_length.setter
    def domain_min_length(self, domain_min_length: int):
        self._min_length_domain = domain_min_length

    @property
    def domain_max_length(self):
        return self._max_length_domain

    @domain_max_length.setter
    def domain_max_length(self, domain_max_length: int):
        self._max_length_domain = domain_max_length

    def _validation_error(self):
        if (self._use_exception == True):
            raise EmailAddressValidationException


    def _character_checker(self, search_string: str, allowed_chars: tuple):
        invalid_character_index = 0
        issues: list = []
        i: int = 0
        for character in [*search_string]:
            if character.upper() in [(char.upper()) for char in allowed_chars]:
                i += 1
                pass
            else:
                issues.append(
                    {"type": "invalid_character", "character": character, "pos": i}
                )
                invalid_character_index += 1
        if len(issues) > 0:
            return False, issues
        else:
            return True, issues

    def _character_missing(self, missing_character: str):
        return {"type": "required character missing", "character": missing_character}

    def validate_email_address(self, email: str):
        result_dict: dict = {}
        splitted: list = []
        if "@" not in email:
            result_dict["basic_pattern"] = [self._character_missing("@")]
            self._validation_error()
            return False, result_dict
        else:
            email_address_part: list = email.split("@")
            splitted.append([email_address_part[0], False])
            if "." not in email_address_part[1]:
                if "basic_pattern" in result_dict:
                    result_dict["basic_pattern"].extend(self._character_missing("."))
                else:
                    result_dict["basic_pattern"] = [self._character_missing(".")]
            else:
                domain_parts = email_address_part[1].split(".")
                if len(domain_parts) > len(self._addressparts) - 1:
                    result_dict["error"] = {
                        "message": "amount of domains do not match given schemata!",
                        "schemata": self._addressparts,
                        "domains": domain_parts,
                        "given_address": email,
                        "count_domains": len(domain_parts),
                        "exspected_count_domains": len(self._addressparts) - 1,
                    }
                    return False, result_dict
                else:
                    i = 1
                    for domain in domain_parts:
                        if len(domain) > self._max_length_domain:
                            result_dict[self._addressparts[i]] = [
                                {
                                    "type": "max_length",
                                    "exspected_length": self._max_length_domain,
                                    "provided_length": len(domain),
                                }
                            ]
                        elif len(domain) < self._min_length_domain:
                            result_dict[self._addressparts[i]] = [
                                {
                                    "type": "min_length",
                                    "exspected_length": self._min_length_domain,
                                    "provided_length": len(domain),
                                }
                            ]
                        splitted.append([domain, True])
                        i += 1
                    else:
                        i = 0
                        for address_chunk in splitted:
                            check_result = self._character_checker(
                                address_chunk[0],
                                self._allowed_characters_email
                                if address_chunk[1] == False
                                else self._allowed_characters_domain,
                            )
                            if check_result[0]:
                                pass
                            else:
                                if self._addressparts[i] in result_dict:
                                    result_dict[self._addressparts[i]].extend(
                                        check_result[1]
                                    )
                                else:
                                    result_dict[self._addressparts[i]] = check_result[1]
                            i += 1
                        if len(result_dict) > 0:
                            self._validation_error()
                            return False, result_dict
                        else:
                            return True, result_dict
