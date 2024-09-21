#!/usr/bin/env python3
"""
Basic Auth module for handling basic authentication
"""

from api.v1.auth.auth import Auth
from typing import TypeVar
from models.user import User
import base64
import binascii


class BasicAuth(Auth):
    """
    BasicAuth class for basic authentication
    """

    def extract_base64_authorization_header(self,
                                            authorization_header: str) -> str:
        """
        Extracts the Base64 part of the Authorization header
        for Basic Authentication

        Args:
            authorization_header (str): The authorization header

        Returns:
            str: The Base64 part of the header or None if invalid
        """
        if authorization_header is None:
            return None
        if not isinstance(authorization_header, str):
            return None
        if not authorization_header.startswith("Basic "):
            return None

        header_array = authorization_header.split(" ")
        if len(header_array) != 2 or header_array[0] != "Basic":
            return None

        return header_array[1]

    def decode_base64_authorization_header(
            self, base64_authorization_header: str) -> str:
        """
        Decodes the Base64 part of the authorization header

        Args:
            base64_authorization_header (str): The Base64 encoded string

        Returns:
            str: The decoded string or None if decoding fails
        """
        if (base64_authorization_header and
                isinstance(base64_authorization_header, str)):
            try:
                encoded_bytes = base64_authorization_header.encode('utf-8')
                decoded_bytes = base64.b64decode(encoded_bytes)
                return decoded_bytes.decode('utf-8')
            except (binascii.Error, UnicodeDecodeError):
                return None
        return None

    def extract_user_credentials(
            self, decoded_base64_authorization_header: str) -> (str, str):
        """
        Extracts user email and password from the Base64 decoded value

        Args:
            decoded_base64_authorization_header (str): The decoded
            Base64 string

        Returns:
            tuple: (user_email, user_password) or (None, None) if invalid
        """
        if (decoded_base64_authorization_header and
                isinstance(decoded_base64_authorization_header, str)):
            if ":" in decoded_base64_authorization_header:
                return tuple(decoded_base64_authorization_header.split(":", 1))
        return (None, None)

    def current_user(self, request=None) -> TypeVar('User'):
        """
        Retrieves the current user based on the authorization header

        Args:
            request: The Flask request object

        Returns:
            User: The current user or None if not found
        """
        auth_header = self.authorization_header(request)
        if auth_header:
            token = self.extract_base64_authorization_header(auth_header)
            if token:
                decoded = self.decode_base64_authorization_header(token)
                if decoded:
                    email, password = self.extract_user_credentials(decoded)
                    if email:
                        return self.user_object_from_credentials(email,
                                                                 password)
        return None

    def user_object_from_credentials(
            self, user_email: str, user_pwd: str) -> TypeVar('User'):
        """
        Returns the User instance based on email and password

        Args:
            user_email (str): The user's email
            user_pwd (str): The user's password

        Returns:
            User: The User instance or None if not found or invalid
        """
        if not user_email or not isinstance(user_email, str):
            return None
        if not user_pwd or not isinstance(user_pwd, str):
            return None
        try:
            users = User.search({'email': user_email})
            if not users:
                return None
            for user in users:
                if user.is_valid_password(user_pwd):
                    return user
        except Exception:
            return None
        return None
