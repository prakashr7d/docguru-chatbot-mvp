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
ORDER_COLUMN_RETURNABLE = "returnable"
ORDER_COLUMN_REFUNDED = "refunded"
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
ORDER_ID_FOR_RETURN = "order_id_for_return"
REASON_FOR_RETURN = "return_a_reason"
TYPE_OF_RETURN = "return_e_type"
REASON_FOR_RETURN_DESCRIPTION = "return_a_reason_description"
PICKUP_ADDRESS_FOR_RETURN = "return_pickup_address"
REFUND_ACCOUNT = "return_refund_account"

# slot counters
EMAIL_TRIES = "email_tries"
OTP_TRIES = "otp_tries"

# Button Titles
CANCEL_ORDER = "Cancel Order"
RETURN_ORDER = "Return Item"
ORDER_STATUS = "Order Status"
PRODUCT_DETAILS = "Product details"
ADD_REVIEW = "Review"
REORDER = "Re-order"
REFUND_ORDER = "Ask For Refund"
SELECT_ORDER = "Select this order"
REPLACE_ORDER = "Replace Item"

# order status
ORDER_PENDING = "order pending"
ORDER_CONFIRMED = "order confirmed"
SHIPPED = "shipped"
CANCELED = "canceled"
DELIVERED = "delivered"
NOT_PICKED = "not picked"
PICKED = "picked"
RECEIVED = "received"
REFUNDED = "refunded"


# Slot counters limits
MAX_OTP_TRIES = 1
MAX_EMAIL_TRIES = 1

# actions name
ACTION_CHECK_ALL_ORDERS = "action_check_all_orders"
ACTION_RETURN_ORDER = "action_show_valid_return_order"
ACTION_CANCEL_ORDER = "action_cancel_order"

# reasons for return
DONT_NEED_THE_PRODUCT = "Don't need the Product"
QUALITY_ISSUES = "Quality issues"
INCORRECT_ITEMS = "Incorrect Items"

# type of payment account
PRIMARY_ACCOUNT = "primary account"
CREDIT_POINTS = "credit points"

# type of return
RETURN_PRODUCT = "Return Product"
REPLACE_PRODUCT = "Replace Product"

# form names
LOGIN_FORM = "login_form"
RETURN_ORDER_FORM = "return_order_form"

# messages
SWITCH_FORM_ASK = "Would you like to switch to {next_action} from {active_form}?"

# form names with intents dictionary
FORM_SLOTS = {
    "return_order_form": [
        ORDER_ID_FOR_RETURN,
        REASON_FOR_RETURN,
        REASON_FOR_RETURN_DESCRIPTION,
        TYPE_OF_RETURN,
        PICKUP_ADDRESS_FOR_RETURN,
        REFUND_ACCOUNT,
    ],
}

# CAROUSEL
POSTBACK = "postback"
TITLE = "title"
PAYLOAD = "payload"
TYPE = "type"
SUBTITLE = "subtitle"
IMAGE_URL = "image_url"
BUTTONS = "buttons"

