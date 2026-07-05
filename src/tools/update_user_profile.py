from langchain_core.tools import tool
from repositories.userdb import users_db


@tool
def update_user_profile(email: str, address: str = None, phone: str = None) -> str:
    """
    Updates the user's profile with additional details such as address and phone number.

    Args:
        email: The email address of the user to update.
        address: The user's street address (optional).
        phone: The user's phone number (optional).

    Returns:
        A confirmation message indicating success or failure.
    """
    if not email:
        return "Error: email is required."

    if address is None and phone is None:
        return "Error: provide at least one field to update (address or phone)."

    success = users_db.update_user_profile(email=email, address=address, phone=phone)

    if not success:
        return f"Error: no user found with email '{email}'."

    updated_fields = []
    if address is not None:
        updated_fields.append(f"address='{address}'")
    if phone is not None:
        updated_fields.append(f"phone='{phone}'")

    return f"User '{email}' updated successfully: {', '.join(updated_fields)}."
