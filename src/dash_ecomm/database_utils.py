from dataclasses import dataclass
from typing import Any, Dict, List, Text

import yaml
from dash_ecomm.constants import (
    DB_FILE,
    DB_USER_COLUMN,
    DB_USER_ORDERS,
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


def get_all_orders() -> List[Dict[Text, Any]]:
    global DATABASE
    return DATABASE.get(DB_USER_ORDERS)


def is_valid_user(useremail: Text) -> bool:
    global DATABASE
    is_valid_user = False
    if useremail in DATABASE[DB_USER_COLUMN]:
        is_valid_user = True
    return is_valid_user


def is_valid_otp(otp: Text, useremail: Text) -> bool:
    global DATABASE
    is_valid_otp = False
    if useremail and useremail in DATABASE[DB_USER_COLUMN]:
        if int(otp) == DATABASE[DB_USER_COLUMN][useremail][USER_PROFILE_COLUMN_OTP]:
            is_valid_otp = True
    return is_valid_otp


def get_user_info_from_db(useremail: Text) -> UserProfile:
    global DATABASE

    if useremail not in DATABASE:
        raise ValueError(f"Useremail {useremail} not found in database")

    profile_info = DATABASE.get(useremail)
    return UserProfile(
        user_id=profile_info[USER_PROFILE_COLUMN_ID],
        email=profile_info[USER_PROFILE_COLUMN_EMAIL],
        first_name=profile_info[USER_PROFILE_COLUMN_FIRSTNAME],
        last_name=profile_info[USER_PROFILE_COLUMN_LASTNAME],
        otp=profile_info[USER_PROFILE_COLUMN_OTP],
    )
