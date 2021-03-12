import logging
import re
from typing import Any, Dict, List, Text, Tuple

import yaml
from dash_ecomm.constants import (
    CUSTOM_UTTERS,
    IS_LOGGED_IN,
    MID_SESSION_GREET_POST_LOGIN,
    MIN_NUM_EVENTS_FOR_MID_SESSION,
    PERSONALIZED_GREET_NEW_SESSION,
    USER_EMAIL,
    USER_FIRST_NAME,
    USER_LAST_NAME,
    USER_OTP,
    get_language,
)
from dash_ecomm.database_utils import get_user_info_from_db, is_valid_user
from rasa_sdk import Action, FormValidationAction, Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher

logger = logging.getLogger(__name__)

# change this to the location of your SQLite file
path_to_db = "actions/example.yml"


def valid_email(email):
    email_regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"  # noqa: W605
    compiled = re.compile(email_regex)
    if re.search(compiled, email):
        logging.info("true " + email)
        return True
    else:
        logging.info("false " + email)
        return False


class PersonalGreet(Action):
    def name(self) -> Text:
        return "personal_greet"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",  # noqa: F821
    ) -> List[Dict[Text, Any]]:
        is_logged_in, user_profile_slot_sets, utter = self.__is_loged_in_user(tracker)
        dispatcher.utter_message(**utter)
        return user_profile_slot_sets

    def __get_useremail_from_token(self, token) -> Text:
        # When we have JWT then write the JWT decode logic here
        return token

    def __validate_user(self, useremail: Text):
        user_profile = None
        if is_valid_user(useremail):
            user_profile = get_user_info_from_db(useremail)
        return user_profile

    def __get_message_template_by_language(
        self, personalized_message_type: Text
    ) -> Text:
        language = get_language()
        return CUSTOM_UTTERS[language][personalized_message_type]

    def __get_greet_message_for_existing_session(
        self, tracker: Tracker, first_name: Text
    ) -> Tuple[bool, Text]:
        session_exists = False
        mid_session_greet = self.__get_message_template_by_language(
            MID_SESSION_GREET_POST_LOGIN
        )
        if len(tracker.events) > MIN_NUM_EVENTS_FOR_MID_SESSION:
            session_exists = True
            mid_session_greet.format(first_name=first_name)
        return session_exists, mid_session_greet

    def __get_personalized_greet_message(
        self, tracker: Tracker, user_first_name: Text = None
    ) -> Text:
        first_name = (
            user_first_name if user_first_name else tracker.get_slot(USER_FIRST_NAME)
        )

        utter = self.__get_message_template_by_language(
            PERSONALIZED_GREET_NEW_SESSION
        ).format(first_name=first_name)
        (
            session_exists,
            mid_session_greet,
        ) = self.__get_greet_message_for_existing_session(tracker, first_name)

        if session_exists:
            utter = mid_session_greet

        return utter

    def __is_loged_in_user(
        self, tracker: Tracker
    ) -> Tuple[bool, List[SlotSet], Dict[Text, Text]]:
        is_logged_in = tracker.get_slot("is_logged_in")
        slot_set = []
        utter = {"template": "utter_generic_greet"}
        if not is_logged_in:
            token = tracker.get_slot("login_token")
            if token:
                user_email = self.__get_useremail_from_token(token)
                user_profile = self.__validate_user(user_email)
                if user_profile:
                    slot_set += [
                        SlotSet(key=USER_EMAIL, value=user_profile.email),
                        SlotSet(key=USER_FIRST_NAME, value=user_profile.first_name),
                        SlotSet(key=USER_LAST_NAME, value=user_profile.last_name),
                        SlotSet(key=IS_LOGGED_IN, value=True),
                        SlotSet(key=USER_OTP, value=user_profile.otp),
                    ]
                    utter = {
                        "text": self.__get_personalized_greet_message(
                            tracker, user_profile.first_name
                        )
                    }
                else:
                    logging.info(
                        "User has logged in to the website but "
                        "email is not present in our database"
                    )
            else:
                logging.info("User has not logged in")

        else:
            logging.info("User has logged in")
            utter = {"text": self.__get_personalized_greet_message(tracker)}

        return is_logged_in, slot_set, utter


class ValidateLoginForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_login_form_action"

    def validate_email(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",  # noqa: F821
    ) -> List[EventType]:
        if value is not None:
            if valid_email(value) is True:
                return {"email": value}
            elif valid_email(value) is False:
                return {"requested_slot": "email"}
        else:
            return {"requested_slot": "email"}


class ActionProductSearch(Action):
    def name(self) -> Text:
        return "action_product_search"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        inStock = 0
        # connect to DB
        database = open(r"actions/example.yml")
        products = yaml.load(database, Loader=yaml.FullLoader)["products"]

        # get slots
        color = tracker.get_slot("color")
        size = tracker.get_slot("size")

        # check for in stock products
        for product in products:
            if color == product["color"] and size == product["size"]:
                inStock += 1

        if inStock > 0:
            # provide in stock message
            dispatcher.utter_message(template="utter_in_stock")
            database.close()
            slots_to_reset = ["size", "color"]
            return [SlotSet(slot, None) for slot in slots_to_reset]
        else:
            # provide out of stock
            dispatcher.utter_message(template="utter_no_stock")
            database.close()
            slots_to_reset = ["size", "color"]
            return [SlotSet(slot, None) for slot in slots_to_reset]


class SurveySubmit(Action):
    def name(self) -> Text:
        return "action_survey_submit"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(template="utter_open_feedback")
        dispatcher.utter_message(template="utter_survey_end")
        return [SlotSet("survey_complete", True)]


class OrderStatus(Action):
    def name(self) -> Text:
        return "action_order_status"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        orderStatus = ""
        # connect to DB
        database = open(r"actions/example.yml")
        orders = yaml.load(database, Loader=yaml.FullLoader)

        # get email slot
        order_email = (tracker.get_slot("verified_email"),)

        # retrieve row based on email
        for order in orders["orders"]:
            if order["email"] == order_email:
                orderStatus = order["status"]
                break

        if orderStatus != "":
            # respond with order status
            dispatcher.utter_message(template="utter_order_status", status=orderStatus)
            database.close()
            return []
        else:
            # db didn't have an entry with this email
            dispatcher.utter_message(template="utter_no_order")
            database.close()
            return []


class CancelOrder(Action):
    def name(self) -> Text:
        return "action_cancel_order"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        orderStatus = ""

        # connect to DB
        database = open("actions/example.yml", "r")
        orders = yaml.load(database, Loader=yaml.FullLoader)

        # get email slot
        order_email = (tracker.get_slot("verified_email"),)

        # retrieve row based on email
        for order in orders["orders"]:
            if order["order_email"] == order_email:
                orderStatus = order["status"]
                break

        if orderStatus != "":
            # change status of entry
            orderStatus = "cancelled"
            for order in orders["orders"]:
                if order["email"] == order_email:
                    order["status"] = orderStatus
            write = open("../src/dash_ecomm/example.yml", "w")
            yaml.dump(orders, write)
            write.close()
            database.close()
            # confirm cancellation
            dispatcher.utter_message(template="utter_order_cancel_finish")
            return []
        else:
            # db didn't have an entry with this email
            dispatcher.utter_message(template="utter_no_order")
            database.close()
            return []


class ReturnOrder(Action):
    def name(self) -> Text:
        return "action_return"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # connect to DB
        orderStatus = ""

        # connect to DB
        database = open(r"actions/example.yml")
        orders = yaml.load(database, Loader=yaml.FullLoader)

        # get email slot
        order_email = (tracker.get_slot("verified_email"),)

        # retrieve row based on email
        for order in orders["orders"]:
            if order["order_email"] == order_email:
                orderStatus = order["status"]
                break
        if orderStatus != "":
            for order in orders["orders"]:
                if order["order_email"] == order_email and orderStatus == "delivered":
                    order["status"] = "returning"
                    break
            write = open("../src/dash_ecomm/example.yml", "w")
            yaml.dump(orders, write)
            write.close()
            database.close()

            # confirm return
            dispatcher.utter_message(template="utter_return_finish")
            return []
        else:
            # db didn't have an entry with this email
            dispatcher.utter_message(template="utter_no_order")
            database.close()
            return []
