from dataclasses import dataclass
from typing import Any, Dict, List, Text

import yaml
from dash_ecomm.constants import (
    DB_FILE,
    DB_USER_COLUMN,
    DB_USER_ORDERS,
    ORDER_COLUMN_EMAIL,
    ORDER_COLUMN_STATUS,
    ORDER_PENDING,
    RETURNING,
    SHIPPED,
    USER_PROFILE_COLUMN_EMAIL,
    USER_PROFILE_COLUMN_FIRSTNAME,
    USER_PROFILE_COLUMN_ID,
    USER_PROFILE_COLUMN_LASTNAME,
    USER_PROFILE_COLUMN_OTP,
)

with open(DB_FILE, "r") as dbf:
    DATABASE = yaml.safe_load(dbf)


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
    for order in orders:
        if order[ORDER_COLUMN_EMAIL] == ordermail and order[ORDER_COLUMN_STATUS] in [
            SHIPPED,
            RETURNING,
            ORDER_PENDING,
        ]:
            order_count += 1
    return order_count
