#!/usr/bin/env python3
"""
DB module for interacting with the database.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from user import Base, User
from typing import TypeVar, Optional, Dict

VALID_FIELDS = ['id', 'email', 'hashed_password', 'session_id', 'reset_token']


class DB:
    """
    DB class for database operations.
    """

    def __init__(self) -> None:
        """
        Initialize a new DB instance.
        """
        self._engine = create_engine("sqlite:///a.db", echo=True)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """
        Memoized session object.
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Adds a new user to the database.

        Args:
            email (str): The user's email.
            hashed_password (str): The user's hashed password.

        Returns:
            User: The created user object.
        """
        if not email or not hashed_password:
            return None
        user = User(email=email, hashed_password=hashed_password)
        session = self._session
        session.add(user)
        session.commit()
        return user

    def find_user_by(self, **kwargs: Dict) -> User:
        """
        Finds a user in the database by specified attributes.

        Args:
            **kwargs: Arbitrary keyword arguments representing user attributes.

        Returns:
            User: The found user object.

        Raises:
            InvalidRequestError: If invalid fields are provided.
            NoResultFound: If no user is found.
        """
        if not kwargs or any(x not in VALID_FIELDS for x in kwargs):
            raise InvalidRequestError
        session = self._session
        try:
            return session.query(User).filter_by(**kwargs).one()
        except Exception:
            raise NoResultFound

    def update_user(self, user_id: int, **kwargs: Dict) -> None:
        """
        Updates a user's attributes in the database.

        Args:
            user_id (int): The user's ID.
            **kwargs: Arbitrary keyword arguments representing user attributes.

        Raises:
            ValueError: If invalid fields are provided.
        """
        session = self._session
        user = self.find_user_by(id=user_id)
        for k, v in kwargs.items():
            if k not in VALID_FIELDS:
                raise ValueError(f"Invalid field: {k}")
            setattr(user, k, v)
        session.commit()
