from dataclasses import dataclass
from typing import Text

import yaml
from dash_ecomm.constants import (
    DB_FILE,
    DB_USER_COLUMN,
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


def is_valid_user(useremail: Text) -> bool:
    global DATABASE
    is_valid_user = False
    if useremail in DATABASE[DB_USER_COLUMN]:
        is_valid_user = True
    return is_valid_user


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
