import json
import logging
from pathlib import Path
from typing import Optional

from models.login_model import LoginData

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).parent.parent / "data" / "users.json"


class UsersDatabase:

    def _read(self) -> dict:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: dict) -> None:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_user_details(self, email: str) -> Optional[LoginData]:
        try:
            data = self._read()
            user = data.get(email)
            if user is None:
                return None
            return LoginData(**user)
        except Exception as ex:
            logger.error("Database Error", exc_info=True)
            raise Exception(f"Database Error: {str(ex)}")

    def update_user_details(self, email: str, token: str, expiration_time: str):
        try:
            data = self._read()
            if email not in data:
                raise ValueError(f"User '{email}' not found.")
            data[email]["access_token"] = token
            data[email]["expiration_time"] = expiration_time
            self._write(data)
        except Exception as ex:
            logger.error("Database Error", exc_info=True)
            raise Exception(f"Database Error: {str(ex)}")

    def update_user_profile(self, email: str, address: str = None, phone: str = None) -> bool:
        try:
            data = self._read()
            if email not in data:
                return False
            if address is not None:
                data[email]["address"] = address
            if phone is not None:
                data[email]["phone"] = phone
            self._write(data)
            return True
        except Exception as ex:
            logger.error("Database Error", exc_info=True)
            raise Exception(f"Database Error: {str(ex)}")


# Module-level singleton
users_db = UsersDatabase()
