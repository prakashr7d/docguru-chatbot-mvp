import os
from pathlib import Path

this_path = Path(os.path.realpath(__file__))

STOP_SHOW_MORE_COUNT = -1
MAX_ITEM_IN_CAROUSEL = 5
MIN_ITEM_IN_CAROUSEL = 0
MIN_NUMBER_ZERO = 0

DB_FILE = str(this_path.parent / "database.yml")
DB_USER_COLUMN = "users"
DB_USER_ORDERS = "orders"


# users
USER_PROFILE_COLUMN_ID = "id"
USER_PROFILE_COLUMN_EMAIL = "user_email"
USER_PROFILE_COLUMN_FIRSTNAME = "first_name"
USER_PROFILE_COLUMN_LASTNAME = "last_name"
USER_PROFILE_COLUMN_OTP = "otp"


# orders
ORDER_COLUMN_ID = "id"
ORDER_COLUMN_EMAIL = "order_email"
ORDER_COLUMN_ORDER_NUMBER = "order_number"
ORDER_COLUMN_PRODUCT_NAME = "product_name"
ORDER_COLUMN_DATE = "order_date"
ORDER_COLUMN_COLOUR = "color"
ORDER_COLUMN_SIZE = "size"
ORDER_COLUMN_STATUS = "status"
ORDER_COLUMN_IMAGE_URL = "image_url"


# Slot Names
LOGIN_TOKEN = "login_token"
USER_EMAIL = "user_email"
USER_FIRST_NAME = "user_first_name"
USER_LAST_NAME = "user_last_name"
IS_LOGGED_IN = "is_logged_in"
USER_OTP = "user_otp"
REQUESTED_SLOT = "requested_slot"
LOGIN_BLOCKED = "login_blocked"
SHOW_MORE_COUNT = "show_more_count"
ACTION_THAT_TRIGGERED_SHOW_MORE = "action_that_triggered_show_more"
IS_SHOW_MORE_TRIGGERED = "is_show_more_triggered"

# slot counters
EMAIL_TRIES = "email_tries"
OTP_TRIES = "otp_tries"


# Button Titles
CANCEL_ORDER = "Cancel Order"
RETURN_ORDER = "Return Order"
TRACK_ORDER = "Track Item"
PRODUCT_DETAILS = "Product details"
ADD_REVIEW = "Review"
REORDER = "Re-order"


# order status
SHIPPED = "shipped"
DELIVERED = "delivered"
ORDER_PENDING = "order pending"
RETURNING = "returning"
CANCELED = "canceled"


# Slot counters limits
MAX_OTP_TRIES = 1
MAX_EMAIL_TRIES = 1


# actions name
ACTION_ORDER_STATUS = "action_order_status"
ACTION_RETURN_ORDER = "action_return_order"
ACTION_CANCEL_ORDER = "action_cancel_order"