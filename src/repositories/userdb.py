import json
import logging
from pathlib import Path
from typing import Optional

from models.login_model import User, UserDetail

logger = logging.getLogger(__name__)

USERS_FILE = Path(__file__).parent.parent / "data" / "users.json"
USER_DETAILS_FILE = Path(__file__).parent.parent / "data" / "user_details.json"


class UsersDatabase:

    def _read_users(self) -> list:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_users(self, data: list) -> None:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _read_details(self) -> list:
        with open(USER_DETAILS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_details(self, data: list) -> None:
        with open(USER_DETAILS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_user_by_email(self, email: str) -> Optional[User]:
        try:
            for item in self._read_users():
                if item["user_email"] == email and item.get("is_active", True):
                    return User(**item)
            return None
        except Exception as ex:
            logger.error("Database Error", exc_info=True)
            raise Exception(f"Database Error: {str(ex)}")

    def update_token(self, user_id: str, token: str, expiration_time: str) -> None:
        try:
            data = self._read_users()
            for item in data:
                if item["user_id"] == user_id:
                    item["jwt_token"] = token
                    item["expiration_time"] = expiration_time
                    self._write_users(data)
                    return
            raise ValueError(f"User '{user_id}' not found.")
        except Exception as ex:
            logger.error("Database Error", exc_info=True)
            raise Exception(f"Database Error: {str(ex)}")

    def update_user_profile(self, user_id: str, address: str = None, phone_no: str = None) -> bool:
        try:
            data = self._read_details()
            for item in data:
                if item["user_id"] == user_id and item.get("is_active", True):
                    if address is not None:
                        item["address"] = address
                    if phone_no is not None:
                        item["phone_no"] = phone_no
                    self._write_details(data)
                    return True
            return False
        except Exception as ex:
            logger.error("Database Error", exc_info=True)
            raise Exception(f"Database Error: {str(ex)}")


users_db = UsersDatabase()
