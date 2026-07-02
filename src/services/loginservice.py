import time
from datetime import datetime
import jwt
import logging

from repositories.userdb import users_db
from models.login_model import LoginResponse, LoginData
from settings import settings

logger = logging.getLogger(__name__)


class LoginService:

    def __init__(self) -> None:
        self.algorithm = settings.ALGORITHM
        self.secret_key = settings.SECRET_KEY
        self.expiration_seconds = settings.TOKEN_EXPIRY_SECONDS

    def login(self, email: str, password: str) -> LoginResponse:
        try:
            userdata: LoginData = users_db.get_user_details(email)

            if userdata is None or userdata.password is None:
                return LoginResponse(
                    status_code=401,
                    data=LoginData(
                        access_token="",
                        expiration_time="",
                        message="User doesn't exist",
                    ),
                )

            if userdata.password != password:
                return LoginResponse(
                    status_code=401,
                    data=LoginData(
                        access_token="",
                        expiration_time="",
                        message="Invalid username or password",
                    ),
                )

            expiry_timestamp = int(time.time()) + self.expiration_seconds
            expiry_str = datetime.fromtimestamp(expiry_timestamp).strftime("%d-%m-%Y %H:%M:%S")

            token = jwt.encode(
                {
                    "user_email": email,
                    "exp": expiry_timestamp,
                },
                self.secret_key,
                algorithm=self.algorithm,
            )

            users_db.update_user_details(email, token, expiry_str)

            return LoginResponse(
                status_code=200,
                data=LoginData(
                    access_token=token,
                    user_id=userdata.user_id,
                    expiration_time=expiry_str,
                    message="Logged in successfully",
                ),
            )

        except Exception as ex:
            logger.error("loginservice error", exc_info=True)
            return LoginResponse(
                status_code=500,
                data=LoginData(
                    access_token="",
                    expiration_time="",
                    message=str(ex),
                ),
            )


# Module-level singleton for use by the router
login_service = LoginService()
