import os

BOT_LANGUAGE = "en"


def get_language():
    global BOT_LANGUAGE
    if "BOT_LANGUAGE" in os.environ:
        BOT_LANGUAGE = os.environ.get("DASH_LANGUAGE")


DB_FILE = "database.yml"
DB_USER_COLUMN = "users"

USER_PROFILE_COLUMN_ID = "id"
USER_PROFILE_COLUMN_EMAIL = "user_email"
USER_PROFILE_COLUMN_FIRSTNAME = "first_name"
USER_PROFILE_COLUMN_LASTNAME = "last_name"
USER_PROFILE_COLUMN_OTP = "otp"


# Slot Names
LOGIN_TOKEN = "login_token"
USER_EMAIL = "user_email"
USER_FIRST_NAME = "user_first_name"
USER_LAST_NAME = "user_last_name"
IS_LOGGED_IN = "is_logged_in"
USER_OTP = "user_otp"


MIN_NUM_EVENTS_FOR_MID_SESSION = 2


# Custom utters keys
PERSONALIZED_GREET_NEW_SESSION = "PERSONALIZED_GREET_NEW_SESSION"
MID_SESSION_GREET_POST_LOGIN = "MID_SESSION_GREET_POST_LOGIN"

# Custom Utters
CUSTOM_UTTERS = {
    "en": {
        PERSONALIZED_GREET_NEW_SESSION: "Hi {first_name}, seems like you have logged in. "
        "Good you see you again. Now I can give you a personalized experience. "
        "How can I help you?",
        MID_SESSION_GREET_POST_LOGIN: "Hi {first_name}, great that you logged in. "
        "Now I can give you a personalized experience.",
    }
}
