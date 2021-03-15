import os
from pathlib import Path

this_path = Path(os.path.realpath(__file__))

DB_FILE = str(this_path.parent / "database.yml")
DB_USER_COLUMN = "users"
DB_USER_ORDERS = "orders"

USER_PROFILE_COLUMN_ID = "id"
USER_PROFILE_COLUMN_EMAIL = "email"
USER_PROFILE_COLUMN_FIRSTNAME = "first_name"
USER_PROFILE_COLUMN_LASTNAME = "last_name"
USER_PROFILE_COLUMN_OTP = "otp"


ORDER_COLUMN_ID = "id"
ORDER_COLUMN_EMAIL = "order_email"
ORDER_COLUMN_ORDER_NUMBER = "first_name"
ORDER_COLUMN_DATE = "order_date"
ORDER_COLUMN_COLOUR = "blue"
ORDER_COLUMN_SIZE = "blue"


# Slot Names
LOGIN_TOKEN = "login_token"
USER_EMAIL = "user_email"
USER_FIRST_NAME = "user_first_name"
USER_LAST_NAME = "user_last_name"
IS_LOGGED_IN = "is_logged_in"
USER_OTP = "user_otp"


# Button Titles
CANCEL_ORDER = "Cancel Order"
RETURN_ORDER = "Return Order"
