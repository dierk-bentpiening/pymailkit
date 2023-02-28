"""
JsonWerkzeug Class
(C) 2023 Dierk-Bent Piening
<dierk-bent.piening@mailbox.org>

"""
import json

class JsonWerkzeug:
    """Tools and helper utilities for  working with JSON
    """

    
    def validatejson(self, jsonstring: str) -> bool:
        """test if a json is valid

        Args:
            jsonstring (str): json inside a string

        Returns:
            bool: True if the json is valid, False if is not valid.
        """
        try:
           json.loads(jsonstring)
           return True
        except ValueError:
            return False
    
   
    def dict2json(self, dictvalue: dict) -> str:
        """Creates a json from a dictionary and validates generated json.
        Args:
            dictvalue (dict): dict which should be exported to json.

        Returns:
            str: validates json as string.
        """
        _json: str = ""
        try:
            _json = json.dumps(dictvalue)
            if self.validatejson(_json):
                return True, _json
        except ValueError:
            return False, _json
            