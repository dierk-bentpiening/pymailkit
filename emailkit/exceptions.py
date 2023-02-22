from . import message
class InvalidTimeStringException(Exception):
    def __init__(self, timestring: str, validation_unit) -> None:
        self._message = f"Exception: Given Timestring'{timestring}' does not match for given schedule unit '{validation_unit}'"

    def __str__(self):
        return self._message

class SmtpBackendNotImplementedException(Exception):
    def __init__(self, backend_name: str):
        self._message = f"Exception: Backend '{backend_name}' is not Implemented!"

        def __str__(self):
            return self._message

class EmailAddressValidationException(Exception):
    def __init__(self, email_address: str):
        self._message = f"Exception: E-Mail Address '{email_address}' is not valid!"

        def __str__(self):
            return self._message

class InvalidMessageTemplate(Exception):
    def __init__(self, template_name, template: str):
        self._message = f"Exception: Template ''{template_name}', is not a valid E-Mail Message Template!"

    def __str__(self):
        return self._message

class NoSenderProvided(Exception):
    def __init__(self, message: message.MailMessage):
        self._message = f"Exception: Message can not be sended, no sender address has been provided\nMessage {message.__str__}"

    def __str__(self):
        return self._message


