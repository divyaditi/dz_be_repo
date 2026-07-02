from typing import Optional
import logging
from models.login_model import LoginData

logger = logging.getLogger(__name__)


class UsersDatabase:

    def __init__(self) -> None:
        # Mock User Database
        self.USERS = {
            "test@gmail.com": {
                "password": "test@123",
                "access_token": "",
                "user_id": "Test24",
                "expiration_time": "",
                "message": "",
            },
        }

    def get_user_details(self, email: str) -> Optional[LoginData]:
        try:
            user = self.USERS.get(email)
            if user is None:
                return None
            return LoginData(**user)
        except Exception as ex:
            logger.error("Database Error", exc_info=True)
            raise Exception(f"Database Error: {str(ex)}")

    def update_user_details(self, email: str, token: str, expiration_time: str):
        try:
            self.USERS[email]["access_token"] = token
            self.USERS[email]["expiration_time"] = expiration_time
        except Exception as ex:
            logger.error("Database Error", exc_info=True)
            raise Exception(f"Database Error: {str(ex)}")


# Module-level singleton so service layer can import it directly
users_db = UsersDatabase()

