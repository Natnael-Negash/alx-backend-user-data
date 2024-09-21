#!/usr/bin/env python3
"""
Auth module for user authentication
"""

from flask import request
from typing import List, TypeVar
from models.user import User


class Auth:
    """Class for handling user authentication"""

    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """Determine if the path requires authentication

        Args:
            path (str): The path to check
            excluded_paths (List[str]): List of paths that do not
                                        require authentication

        Returns:
            bool: True if authentication is required, False otherwise
        """
        if not path or not excluded_paths:
            return True

        if path[-1] == '/':
            path = path[:-1]

        for excluded_path in excluded_paths:
            if excluded_path.endswith('*'):
                if path.startswith(excluded_path[:-1]):
                    return False
            if excluded_path.endswith('/'):
                excluded_path = excluded_path[:-1]
            if path == excluded_path:
                return False

        return True

    def authorization_header(self, request=None) -> str:
        """Get the authorization header from the request

        Args:
            request: The Flask request object

        Returns:
            str: The authorization header if present, None otherwise
        """
        if request is None:
            return None
        return request.headers.get('Authorization')

    def current_user(self, request=None) -> TypeVar('User'):
        """Get the current user

        Args:
            request: The Flask request object

        Returns:
            User: The current user, None by default
        """
        return None
