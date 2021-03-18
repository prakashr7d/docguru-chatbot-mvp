import logging
from typing import Any, Dict, List, Text, Tuple

from dash_ecomm import generic_utils
from dash_ecomm.constants import (
    CANCEL_ORDER,
    EMAIL_TRIES,
    IS_LOGGED_IN,
    LOGIN_BLOCKED,
    MAX_EMAIL_TRIES,
    MAX_OTP_TRIES,
    ORDER_COLUMN_EMAIL,
    ORDER_COLUMN_IMAGE_URL,
    ORDER_COLUMN_PRODUCT_NAME,
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

    def __set_unblock_reminder(self, tracker: Tracker):
        set_reminder = True if tracker.get_slot(EMAIL_TRIES) > 0 else False

        reminder_events = []
        if set_reminder:
            logger.debug("*" * 100)
            logger.debug(set_reminder)
            timestamp = generic_utils.get_unblock_timestamp()
            login_event = events.ReminderScheduled(
                intent_name="EXTERNAL_unblock_login",
                trigger_date_time=timestamp,
                name="login_unblock",
                kill_on_user_message=False,
            )
            reminder_events.append(login_event)
        return reminder_events

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
        slot_set = []
        if login_blocked:
            dispatcher.utter_message(template="utter_login_blocked")
            dispatcher.utter_message(template="utter_login_blocked_duration")
            dispatcher.utter_message(template="utter_login_via_website")

            reminder_events = self.__set_unblock_reminder(tracker)
            slot_set += [SlotSet(EMAIL_TRIES, 0), SlotSet(OTP_TRIES, 0)]
            slot_set += reminder_events
        else:
            user_email = tracker.get_slot(USER_EMAIL)
            user_profile = PersonalGreet.validate_user(user_email)
            if user_profile and not tracker.get_slot(IS_LOGGED_IN):
                dispatcher.utter_message(template="utter_login_success")
                slot_set += [
                    SlotSet(key=USER_EMAIL, value=user_profile.email),
                    SlotSet(key=USER_FIRST_NAME, value=user_profile.first_name),
                    SlotSet(key=USER_LAST_NAME, value=user_profile.last_name),
                    SlotSet(key=IS_LOGGED_IN, value=True),
                    SlotSet(key=USER_OTP, value=user_profile.otp),
                ]
            elif user_profile and tracker.get_slot(IS_LOGGED_IN):
                pass
            else:
                dispatcher.utter_message(template="utter_login_failed")
        logger.debug(slot_set)
        return slot_set


class ValidateLoginForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_login_form"

    def __utter_message_and_slots(
        self, email: Text, slots: Dict[Text, Text]
    ) -> Tuple[Text, Dict]:
        slots = slots if slots else {}
        slots[USER_EMAIL] = None
        if email is None:
            utter = "utter_email_not_valid_prompt"
        elif not is_valid_user(email):
            utter = "utter_user_email_not_registered"
            slots[REQUESTED_SLOT] = None
            # slots.pop(USER_EMAIL)
        else:
            utter = "utter_user_email_not_valid"
        return utter, slots

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
            returned_slots = {USER_EMAIL: value}
        elif email_tries >= MAX_EMAIL_TRIES:
            returned_slots = {
                REQUESTED_SLOT: None,
                LOGIN_BLOCKED: True,
                USER_EMAIL: None,
            }
        else:
            email_tries += 1
            utter, returned_slots = self.__utter_message_and_slots(
                value, returned_slots
            )
            logger.debug(returned_slots)
            dispatcher.utter_message(template=utter)
            returned_slots[EMAIL_TRIES] = email_tries
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
                returned_slots = {
                    REQUESTED_SLOT: None,
                    LOGIN_BLOCKED: True,
                    USER_OTP: None,
                }
            else:
                otp_tries += 1
                dispatcher.utter_message(template="utter_incorrect_otp")
                returned_slots = {USER_OTP: None, OTP_TRIES: otp_tries}
        return returned_slots


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
        events.ReminderCancelled(name="login_unblock")
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


class OrderStatus(Action):
    def name(self) -> Text:
        return "action_order_status"

    def __add_track_item_button(
        self, order: Dict[Text, Any], carousel: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        if order[ORDER_COLUMN_STATUS] in [SHIPPED, RETURNING]:
            carousel["buttons"].append(
                {"title": TRACK_ORDER, "payload": "", "type": "postback"}
            )

    def __create_order_carousel(self, orders: List[Dict[Text, Any]]) -> Dict[Text, Any]:
        carousel = {
            "type": "template",
            "payload": {"template_type": "generic", "elements": []},
        }
        for order in orders:
            carousel_element = {
                "title": order[ORDER_COLUMN_PRODUCT_NAME],
                "subtitle": f"Status: {order[ORDER_COLUMN_STATUS]}",
                "image_url": order[ORDER_COLUMN_IMAGE_URL],
                "buttons": [
                    {
                        "title": PRODUCT_DETAILS,
                        "payload": "",
                        "type": "postback",
                    },
                    {
                        "title": CANCEL_ORDER,
                        "payload": "",
                        "type": "postback",
                    },
                ],
            }
            self.__add_track_item_button(order, carousel_element)
            carousel["payload"]["elements"].append(carousel_element)
        return carousel

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[SlotSet]:
        order_email = tracker.get_slot(USER_EMAIL)

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
