import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Text

import yaml
from dash_ecomm.constants import (
    DB_FILE,
    DB_USER_COLUMN,
    DB_USER_ORDERS,
    DELIVERED,
    ORDER_COLUMN_EMAIL,
    ORDER_COLUMN_ID,
    ORDER_COLUMN_REFUNDED,
    ORDER_COLUMN_RETURNABLE,
    ORDER_COLUMN_STATUS,
    USER_PROFILE_COLUMN_EMAIL,
    USER_PROFILE_COLUMN_FIRSTNAME,
    USER_PROFILE_COLUMN_ID,
    USER_PROFILE_COLUMN_LASTNAME,
    USER_PROFILE_COLUMN_OTP,
)
from dash_ecomm.generic_utils import is_valid_order_id

with open(DB_FILE, "r") as dbf:
    DATABASE = yaml.safe_load(dbf)

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    email: Text
    user_id: int
    first_name: Text
    last_name: Text
    otp: int


@dataclass
class Order:
    order_date: str
    order_number: int
    order_email: Text
    name: Text
    color: Text
    size: Text
    status: Text
    image_url: Text


def get_all_orders_from_email(order_email: Text) -> List[Dict[Text, Any]]:
    global DATABASE

    orders = []
    for order in DATABASE[DB_USER_ORDERS]:
        if order[ORDER_COLUMN_EMAIL] == order_email:
            orders.append(order)

    return orders


def get_order_by_order_id(order_id: int):
    global DATABASE

    for order in DATABASE[DB_USER_ORDERS]:
        if order[ORDER_COLUMN_ID] == order_id:
            return order
    return False


def is_valid_user(useremail: Text) -> bool:
    global DATABASE

    is_valid_user = False

    if useremail in DATABASE[DB_USER_COLUMN]:
        is_valid_user = True

    return is_valid_user


def is_valid_otp(otp: Text, useremail: Text) -> bool:
    global DATABASE
    valid_otp = False
    if useremail in DATABASE[DB_USER_COLUMN]:
        if str(otp) == DATABASE[DB_USER_COLUMN][useremail][USER_PROFILE_COLUMN_OTP]:
            valid_otp = True
    return valid_otp


def get_user_info_from_db(useremail: Text) -> UserProfile:
    global DATABASE

    if useremail not in DATABASE[DB_USER_COLUMN]:
        raise ValueError(f"Useremail {useremail} not found in database")

    profile_info = DATABASE[DB_USER_COLUMN][useremail]
    return UserProfile(
        user_id=profile_info[USER_PROFILE_COLUMN_ID],
        email=profile_info[USER_PROFILE_COLUMN_EMAIL],
        first_name=profile_info[USER_PROFILE_COLUMN_FIRSTNAME],
        last_name=profile_info[USER_PROFILE_COLUMN_LASTNAME],
        otp=profile_info[USER_PROFILE_COLUMN_OTP],
    )


def get_valid_order_count(ordermail: Text) -> int:
    global DATABASE

    order_count = 0
    orders = get_all_orders_from_email(ordermail)
    for selected_order in orders:
        if selected_order[ORDER_COLUMN_EMAIL] == ordermail:
            order_count += 1
    return order_count


def get_valid_order_return(ordermail: Text) -> List[Dict[Text, Any]]:
    global DATABASE

    delivered_order = []
    orders = get_all_orders_from_email(ordermail)
    for selected_order in orders:
        if (
            selected_order[ORDER_COLUMN_STATUS] == DELIVERED
            and selected_order[ORDER_COLUMN_RETURNABLE]
        ):
            delivered_order.append(selected_order)
    return delivered_order


def validate_order_id(order_id: Text, order_email: Text) -> bool:
    global DATABASE

    if is_valid_order_id(order_id):
        for selected_order in DATABASE[DB_USER_ORDERS]:
            if (
                order_id in selected_order[ORDER_COLUMN_ID]
                and order_email == selected_order[ORDER_COLUMN_EMAIL]
            ):
                return True
    else:
        return False


def update_order_status(status: Text, order_id: Text):
    global DATABASE

    for selected_order in DATABASE[DB_USER_ORDERS]:
        if order_id in selected_order[ORDER_COLUMN_ID]:
            selected_order[ORDER_COLUMN_STATUS] = status
            selected_order[ORDER_COLUMN_RETURNABLE] = False
            selected_order[ORDER_COLUMN_REFUNDED] = False
    with open(DB_FILE, "w+") as dbfw:
        yaml.dump(DATABASE, dbfw)
