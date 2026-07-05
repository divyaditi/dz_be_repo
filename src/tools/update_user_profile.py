from typing import Optional
from langchain_core.tools import tool
from repositories.userdb import users_db


@tool
def update_user_profile(email: str, address: Optional[str] = None, phone: Optional[str] = None) -> dict:
    """
    Updates the user's profile with address and/or phone number.

    Args:
        email:   The email address of the user to update.
        address: The user's street address (optional).
        phone:   The user's phone number (optional).

    Returns:
        {"email": ..., "updated_fields": [...]}
        or {"error": "..."}
    """
    if not email:
        return {"error": "email is required"}

    if address is None and phone is None:
        return {"error": "provide at least one field to update: address or phone"}

    success = users_db.update_user_profile(email=email, address=address, phone=phone)

    if not success:
        return {"error": f"user '{email}' not found"}

    updated_fields = []
    if address is not None:
        updated_fields.append("address")
    if phone is not None:
        updated_fields.append("phone")

    return {"email": email, "updated_fields": updated_fields}
