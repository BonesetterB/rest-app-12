from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import config
import pickle
import redis

def hash_for_user(email:str):
    """
    Hash the email to create a user hash.

    :param email: The email to be hashed.
    :type email: str
    :return: Hashed user representation.
    :rtype: str
    """
    return f"user:{email}"

class Auth:
    """
    Class for authentication-related functionalities.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY =config.secret_key
    ALGORITHM = config.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
    cache = redis.Redis(host='localhost', port=6379, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
        Verify if the provided plain password matches the hashed password.

        :param plain_password: The plain password to be verified.
        :type plain_password: str
        :param hashed_password: The hashed password to be compared against.
        :type hashed_password: str
        :return: True if passwords match, else False.
        :rtype: bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Generate a hash for the provided password.

        :param password: The password to be hashed.
        :type password: str
        :return: Hashed password.
        :rtype: str
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create an access token for authentication.

        :param data: Data to be encoded into the token.
        :type data: dict
        :param expires_delta: Expiry time for the token (in seconds).
        :type expires_delta: float, optional
        :return: Encoded access token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create a refresh token for authentication.

        :param data: Data to be encoded into the token.
        :type data: dict
        :param expires_delta: Expiry time for the token (in seconds).
        :type expires_delta: float, optional
        :return: Encoded refresh token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Decode a refresh token and retrieve the email associated with it.

        :param refresh_token: The refresh token to be decoded.
        :type refresh_token: str
        :return: Email from the token.
        :rtype: str
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    def create_email_token(self, data: dict):
        """
        Create a token for email verification.

        :param data: Data to be encoded into the token.
        :type data: dict
        :return: Encoded email verification token.
        :rtype: str
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        Retrieve the email from an email verification token.

        :param token: The email verification token to be decoded.
        :type token: str
        :return: Decoded email from the token.
        :rtype: str
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        """
        Get the current authenticated user from the access token.

        :param token: The access token for authentication.
        :type token: str
        :param db: The database session.
        :type db: AsyncSession
        :return: Current authenticated user.
        :rtype: User
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user_hash=hash_for_user(email)
        user = self.cache.get(user_hash)
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.cache.set(user_hash, pickle.dumps(user))
            self.cache.expire(user_hash, 900)
        else:
            user = pickle.loads(user)

        return user


auth_service = Auth()