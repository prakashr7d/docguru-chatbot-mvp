import logging
from typing import Any, Dict, List, Text, Tuple

import yaml
from dash_ecomm import generic_utils
from dash_ecomm.constants import (
    EMAIL_TRIES,
    IS_LOGGED_IN,
    LOGIN_BLOCKED,
    MAX_EMAIL_TRIES,
    MAX_OTP_TRIES,
    ORDER_COLUMN_COLOUR,
    ORDER_COLUMN_EMAIL,
    ORDER_COLUMN_IMAGE_URL,
    ORDER_COLUMN_PRODUCT_NAME,
    ORDER_COLUMN_SIZE,
    ORDER_COLUMN_STATUS,
    ORDER_PENDING,
    OTP_TRIES,
    PRODUCT_DETAILS,
    REQUESTED_SLOT,
    RETURNING,
    SHIPPED,
    TRACK_ORDER,
    USER_EMAIL,
    USER_FIRST_NAME,
    USER_LAST_NAME,
    USER_OTP,
)
from dash_ecomm.database_utils import (
    get_all_orders,
    get_user_info_from_db,
    is_valid_otp,
    is_valid_user,
)
from rasa_sdk import Action, FormValidationAction, Tracker, events
from rasa_sdk.events import AllSlotsReset, EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher

logger = logging.getLogger(__name__)


"""
TODO 1: Check what to do when logout from website and not from bot
TODO 2: Add logout feature in bot
TODO 3: Check for Reminder Schedule and how it will work
TODO 4: Make Rules for login blocked with every login required forms
TODO 4: On login via website unblock user if blocked already
"""


class PersonalGreet(Action):
    def name(self) -> Text:
        return "personal_greet"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",  # noqa: F821
    ) -> List[Dict[Text, Any]]:
        is_logged_in, user_profile_slot_sets, utter = self.__is_logged_in_user(tracker)
        dispatcher.utter_message(**utter)
        print(tracker.sender_id)
        return user_profile_slot_sets

    @staticmethod
    def __get_useremail_from_token(token) -> Text:
        # When we have JWT then write the JWT decode logic here
        return token

    @staticmethod
    def validate_user(useremail: Text):
        user_profile = None
        if is_valid_user(useremail):
            user_profile = get_user_info_from_db(useremail)
        return user_profile

    def __get_user_token_from_metadata(self, tracker: Tracker) -> Text:
        user_token = None
        events = tracker.current_state()["events"]
        user_events = []
        for e in events:
            if e["event"] == "user":
                user_events.append(e)
        if tracker.events:
            user_token = user_events[-1]["metadata"].get("user_token", None)
        return user_token

    def __is_logged_in_user(
        self, tracker: Tracker
    ) -> Tuple[bool, List[SlotSet], Dict[Text, Text]]:
        is_logged_in = tracker.get_slot("is_logged_in")
        slot_set = []
        utter = {"template": "utter_generic_greet"}
        if not is_logged_in:
            token = self.__get_user_token_from_metadata(tracker)
            if token:
                user_email = self.__get_useremail_from_token(token)
                user_profile = self.validate_user(user_email)
                if user_profile:
                    slot_set += [
                        SlotSet(key=USER_EMAIL, value=user_profile.email),
                        SlotSet(key=USER_FIRST_NAME, value=user_profile.first_name),
                        SlotSet(key=USER_LAST_NAME, value=user_profile.last_name),
                        SlotSet(key=IS_LOGGED_IN, value=True),
                        SlotSet(key=USER_OTP, value=user_profile.otp),
                    ]
                    utter = {
                        "template": "utter_personalized_greet_new_session",
                        "first_name": user_profile.first_name,
                    }
                else:
                    slot_set += self.__empty_user_slots()
                    logging.info(
                        "User has logged in to the website but "
                        "email is not present in our database"
                    )
            else:
                slot_set += self.__empty_user_slots()
                logging.info("User has not logged in")
        else:
            logging.info("User has logged in")
            utter = {
                "template": "utter_personalized_greet_new_session",
                "first_name": tracker.get_slot(USER_FIRST_NAME),
            }

        return is_logged_in, slot_set, utter

    def __empty_user_slots(self):
        slot_set = [
            SlotSet(key=USER_EMAIL, value=None),
            SlotSet(key=USER_FIRST_NAME, value=None),
            SlotSet(key=USER_LAST_NAME, value=None),
            SlotSet(key=IS_LOGGED_IN, value=False),
            SlotSet(key=USER_OTP, value=None),
        ]
        return slot_set


class LoginFormAction(Action):
    def name(self) -> Text:
        return "action_login_form"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",  # noqa: F821
    ) -> List[Dict[Text, Any]]:
        """
        check if login blocked then
            utter login blocked
            utter you can try logining through chatbot after k minutes
            utter you can always login through website anytime
            :return set reminder unblock login after k minutes, slotset email_tries, otp_tries to 0,
        check else
          usual login prompt
        """
        login_blocked = tracker.get_slot(LOGIN_BLOCKED)
        if login_blocked:
            dispatcher.utter_message(template="utter_login_blocked")
            dispatcher.utter_message(template="utter_login_blocked_duration")
            dispatcher.utter_message(template="utter_login_via_website")
            timestamp = generic_utils.get_unblock_timestamp()
            login_event = events.ReminderScheduled(
                intent_name="EXTERNAL_unblock_login",
                trigger_date_time=timestamp,
                name="login_unblock",
            )
            return [SlotSet(EMAIL_TRIES, 0), SlotSet(OTP_TRIES, 0), login_event]
        else:
            user_email = tracker.get_slot(USER_EMAIL)
            user_profile = PersonalGreet.validate_user(user_email)
            slot_set = []
            if user_profile:
                if not tracker.get_slot(IS_LOGGED_IN):
                    dispatcher.utter_message(template="utter_login_success")
                slot_set += [
                    SlotSet(key=USER_EMAIL, value=user_profile.email),
                    SlotSet(key=USER_FIRST_NAME, value=user_profile.first_name),
                    SlotSet(key=USER_LAST_NAME, value=user_profile.last_name),
                    SlotSet(key=IS_LOGGED_IN, value=True),
                    SlotSet(key=USER_OTP, value=user_profile.otp),
                ]
            else:
                dispatcher.utter_message(template="utter_login_failed")
            return slot_set


class ValidateLoginForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_login_form"

    def validate_user_email(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",  # noqa: F821
    ) -> List[EventType]:
        email_tries = tracker.get_slot(EMAIL_TRIES)
        returned_slots = {}
        if value is not None and is_valid_user(value):
            logger.debug(f"{value} is a valid user")
            returned_slots = {USER_EMAIL: value}
        else:
            if email_tries >= MAX_EMAIL_TRIES:
                logger.debug("inside max email tries")
                returned_slots = {REQUESTED_SLOT: None, LOGIN_BLOCKED: True}
            else:
                email_tries += 1
                utter = self.__utter_email_validation_message(value)
                dispatcher.utter_message(template=utter)
                returned_slots = {USER_EMAIL: None, EMAIL_TRIES: email_tries}
        return returned_slots

    def validate_user_otp(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",  # noqa: F821
    ) -> List[EventType]:
        email = tracker.get_slot(USER_EMAIL)
        otp_tries = tracker.get_slot(OTP_TRIES)
        if value is not None and is_valid_otp(value, email):
            logger.debug(f"{value} is a valid user")
            returned_slots = {USER_OTP: value}
        else:
            if otp_tries >= MAX_OTP_TRIES:
                logger.debug("inside max email tries")
                returned_slots = {REQUESTED_SLOT: None, LOGIN_BLOCKED: True}
            else:
                otp_tries += 1
                dispatcher.utter_message(template="utter_incorrect_otp")
                returned_slots = {USER_OTP: None, OTP_TRIES: otp_tries}
        return returned_slots

    def __utter_email_validation_message(
        self,
        email: Text,
    ) -> Text:
        if is_valid_user(email) is False:
            utter = "utter_user_email_not_registered"
        else:
            utter = "utter_user_email_not_valid"
        return utter


class ActionLoginUnblock(Action):
    def name(self) -> Text:
        return "action_unblock_login"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",  # noqa: F821
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="utter_login_unblocked")
        return [SlotSet(LOGIN_BLOCKED, False)]


class ActionLogout(Action):
    def name(self) -> Text:
        return "action_logout"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",  # noqa: F821
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="utter_logout")
        return [AllSlotsReset()]


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

    def __create_order_carousel(self, orders: List[Dict[Text, Any]]) -> Dict[Text, Any]:
        carousel = {
            "type": "template",
            "payload": {"template_type": "generic", "elements": []},
        }
        for order in orders:
            button_title = ""
            if ORDER_PENDING == order[ORDER_COLUMN_STATUS]:
                button_title = PRODUCT_DETAILS
            elif order[ORDER_COLUMN_STATUS] in [SHIPPED, RETURNING]:
                button_title = TRACK_ORDER
            carousel["payload"]["elements"].append(
                {
                    "title": order[ORDER_COLUMN_PRODUCT_NAME],
                    "subtitle": f"Size: {order[ORDER_COLUMN_SIZE]}\n"
                    f"Color: {order[ORDER_COLUMN_COLOUR]}\nStatus: {order[ORDER_COLUMN_STATUS]}",
                    "image_url": order[ORDER_COLUMN_IMAGE_URL],
                    "buttons": [
                        {
                            "title": button_title,
                            "payload": "",
                            "type": "postback",
                        },
                        {
                            "title": PRODUCT_DETAILS,
                            "payload": "",
                            "type": "postback",
                        },
                    ],
                }
            )
        return carousel

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[SlotSet]:
        # get email slot
        order_email = tracker.get_slot("user_email")

        # retrieve row based on email
        current_orders = []
        for order in get_all_orders():
            if order[ORDER_COLUMN_EMAIL] == order_email and order[
                ORDER_COLUMN_STATUS
            ] in [SHIPPED, RETURNING, ORDER_PENDING]:
                current_orders.append(order)

        if not current_orders:
            dispatcher.utter_message(template="utter_no_open_orders")

        else:
            dispatcher.utter_message(template="utter_open_current_orders")
            dispatcher.utter_message(
                attachment=self.__create_order_carousel(current_orders)
            )
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
        order_email = (tracker.get_slot("user_email"),)

        # retrieve row based on email
        for order in get_all_orders():
            if order[ORDER_COLUMN_EMAIL] == order_email:
                orderStatus = order[ORDER_COLUMN_STATUS]
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
