from typing import Optional
from langchain_core.tools import tool
from repositories.userdb import users_db


@tool
def update_user_profile(user_id: str, address: Optional[str] = None, phone_no: Optional[str] = None) -> dict:
    """
    Updates the user's profile with address and/or phone number.

    Args:
        user_id:  The unique ID of the user to update.
        address:  The user's street address (optional).
        phone_no: The user's phone number (optional).

    Returns:
        {"tool": "update_user_profile", "data": {"user_id", "updated_fields": [...]}}
    """
    if not user_id:
        return {"tool": "update_user_profile", "data": {"message": "user_id is required"}}

    if address is None and phone_no is None:
        return {"tool": "update_user_profile", "data": {"message": "provide at least one field: address or phone_no"}}

    success = users_db.update_user_profile(user_id=user_id, address=address, phone_no=phone_no)

    if not success:
        return {"tool": "update_user_profile", "data": {"message": f"user_id '{user_id}' not found"}}

    updated_fields = []
    if address is not None:
        updated_fields.append("address")
    if phone_no is not None:
        updated_fields.append("phone_no")

    return {
        "tool": "update_user_profile",
        "data": {"user_id": user_id, "updated_fields": updated_fields},
    }
