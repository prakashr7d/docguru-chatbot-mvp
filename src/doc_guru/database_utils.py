import yaml
import os
from pathlib import Path
from typing import Text, Any
from dataclasses import dataclass
this_path = Path(os.path.realpath(__file__))
DB_FILE = str(this_path.parent / "database.yml")
with open(DB_FILE, "r") as dbf:
    DATABASE = yaml.safe_load(dbf)


@dataclass
class UserProfile:
    email: Text
    user_id: int
    first_name: Text
    last_name: Text
    otp: int


def give_step(step: Text, service: Text):
    if int(step) < len(DATABASE[service])+1:
        return DATABASE[service]['step'+str(step)]
    else:
        return False


def give_current_step(user: Text, service: Text):
    return DATABASE['user'][user][service]


def update_step_value(user: Text, service: Text, value: Any):
    if int(value) > len(DATABASE[service]):
        value = '1'
    DATABASE['user'][user][service] = value
    with open(DB_FILE, 'w') as dbf:
        yaml.safe_dump(DATABASE, dbf)
    return True


def is_valid_user(useremail: Text) -> bool:
    global DATABASE

    is_valid_user = False

    if useremail in DATABASE['user']:
        is_valid_user = True

    return is_valid_user


def is_valid_otp(otp: Text, useremail: Text) -> bool:
    global DATABASE
    valid_otp = False
    if useremail in DATABASE['user']:
        if str(otp) == str(DATABASE['user'][useremail]['otp']):
            valid_otp = True
    return valid_otp

def get_user_info_from_db(useremail: Text) -> UserProfile:
    global DATABASE

    if useremail not in DATABASE['user']:
        raise ValueError(f"Useremail {useremail} not found in database")

    profile_info = DATABASE['user'][useremail]
    return UserProfile(
        user_id=profile_info['id'],
        email=profile_info['email'],
        first_name=profile_info['firstname'],
        last_name=profile_info['lastname'],
        otp=profile_info['otp'],
    )

