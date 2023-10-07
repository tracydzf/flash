import base64
import json


class Bytes:
    @staticmethod
    def str_to_bytes(string: str):
        """
        converts string data to bytes

        @returns: string bytes
        """
        return string.encode("utf-8")

    @staticmethod
    def object_to_bytes(obj: object):
        """
        coverts object to bytes

        @returns: object bytes
        """
        return json.dumps(obj).encode('utf-8')

    @staticmethod
    def encode_bytes(data):
        """
        encodes bytes data to base64

        @returns: encoded data
        """
        return base64.b64encode(data)

    @staticmethod
    def decode_bytes(data):
        """
        decodes bytes data from base64

        @return: decoded data
        """
        return base64.b64decode(data)
