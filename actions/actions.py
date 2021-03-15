import logging
from typing import Any, Dict, List, Text, Tuple

import yaml
from dash_ecomm.constants import (
    CANCEL_ORDER,
    IS_LOGGED_IN,
    ORDER_COLUMN_COLOUR,
    ORDER_COLUMN_EMAIL,
    ORDER_COLUMN_ID,
    ORDER_COLUMN_IMAGE_URL,
    ORDER_COLUMN_PRODUCT_NAME,
    ORDER_COLUMN_STATUS,
    RETURN_ORDER,
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
from rasa_sdk import Action, FormValidationAction, Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher

logger = logging.getLogger(__name__)


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
                    logging.info(
                        "User has logged in to the website but "
                        "email is not present in our database"
                    )
            else:
                logging.info("User has not logged in")
        else:
            logging.info("User has logged in")
            utter = {
                "template": "utter_personalized_greet_new_session",
                "first_name": tracker.get_slot(USER_FIRST_NAME),
            }

        return is_logged_in, slot_set, utter


class LoginFormAction(Action):
    def name(self) -> Text:
        return "login_form_action"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",  # noqa: F821
    ) -> List[Dict[Text, Any]]:
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
        if value is not None:
            if is_valid_user(value):
                logger.debug(f"{value} is a valid user")
                return {USER_EMAIL: value}
            else:
                dispatcher.utter_message(template="utter_user_email_not_registered")
                return {USER_EMAIL: None}
        else:
            dispatcher.utter_message(template="utter_user_email_not_valid")
            return {USER_EMAIL: None}

    def validate_user_otp(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",  # noqa: F821
    ) -> List[EventType]:
        if value is not None:
            email = tracker.get_slot(USER_EMAIL)
            if is_valid_otp(value, email):
                return {USER_OTP: value}
            else:
                return {USER_OTP: None}
        else:
            return {USER_OTP: None}


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
            carousel["payload"]["elements"].append(
                {
                    "title": order[ORDER_COLUMN_PRODUCT_NAME],
                    "subtitle": order[ORDER_COLUMN_COLOUR],
                    "image_url": order[ORDER_COLUMN_IMAGE_URL],
                    "buttons": [
                        {
                            "title": CANCEL_ORDER,
                            "payload": f'/order_cancel{{"order_id": "{order[ORDER_COLUMN_ID]}"}}',
                            "type": "postback",
                        },
                        {
                            "title": RETURN_ORDER,
                            "payload": f'/return{{"order_id": "{order[ORDER_COLUMN_ID]}"}}',
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
            if (
                order[ORDER_COLUMN_EMAIL] == order_email
                and order[ORDER_COLUMN_STATUS] == "shipped"
            ):
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
