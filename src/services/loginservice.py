import time
from datetime import datetime
import jwt
import logging

from repositories.userdb import users_db
from models.login_model import LoginResponse
from settings import settings

logger = logging.getLogger(__name__)


class LoginService:

    def __init__(self) -> None:
        self.algorithm = settings.ALGORITHM
        self.secret_key = settings.SECRET_KEY
        self.expiration_seconds = settings.TOKEN_EXPIRY_SECONDS

    def login(self, email: str, password: str) -> LoginResponse:
        try:
            user = users_db.get_user_by_email(email)

            if user is None:
                return LoginResponse(status_code=401, message="User doesn't exist")

            if user.password != password:
                return LoginResponse(status_code=401, message="Invalid username or password")

            # Check if existing token is still valid
            if user.jwt_token:
                try:
                    jwt.decode(user.jwt_token, self.secret_key, algorithms=[self.algorithm])
                    return LoginResponse(
                        status_code=200,
                        user_id=user.user_id,
                        jwt_token=user.jwt_token,
                        expiration_time=user.expiration_time,
                        message="Token is already valid",
                    )
                except jwt.ExpiredSignatureError:
                    pass
                except jwt.InvalidTokenError:
                    pass

            # Issue new token
            expiry_timestamp = int(time.time()) + self.expiration_seconds
            expiry_str = datetime.fromtimestamp(expiry_timestamp).strftime("%d-%m-%Y %H:%M:%S")

            token = jwt.encode(
                {"user_id": user.user_id, "exp": expiry_timestamp},
                self.secret_key,
                algorithm=self.algorithm,
            )

            users_db.update_token(user.user_id, token, expiry_str)

            return LoginResponse(
                status_code=200,
                user_id=user.user_id,
                jwt_token=token,
                expiration_time=expiry_str,
                message="Logged in successfully",
            )

        except Exception as ex:
            logger.error("loginservice error", exc_info=True)
            return LoginResponse(status_code=500, message=str(ex))


login_service = LoginService()
