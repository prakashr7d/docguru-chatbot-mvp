import logging
from typing import Any, Dict, List, Text, Tuple

from dash_ecomm import generic_utils
from dash_ecomm.constants import (
    ACTION_CANCEL_ORDER,
    ACTION_ORDER_STATUS,
    ACTION_RETURN_ORDER,
    ACTION_THAT_TRIGGERED_SHOW_MORE,
    ADD_REVIEW,
    CREDIT_POINTS,
    DONT_NEED_THE_PRODUCT,
    EMAIL_TRIES,
    INCORRECT_ITEMS,
    IS_LOGGED_IN,
    IS_SHOW_MORE_TRIGGERED,
    LOGIN_BLOCKED,
    MAX_EMAIL_TRIES,
    MAX_ITEM_IN_CAROUSEL,
    MAX_OTP_TRIES,
    MIN_ITEM_IN_CAROUSEL,
    MIN_NUMBER_ZERO,
    ORDER_COLUMN_EMAIL,
    ORDER_COLUMN_ID,
    ORDER_COLUMN_IMAGE_URL,
    ORDER_COLUMN_PRODUCT_NAME,
    ORDER_COLUMN_STATUS,
    ORDER_ID_FOR_RETURN,
    ORDER_PENDING,
    OTP_TRIES,
    PICKUP_ADDRESS_FOR_RETURN,
    PRIMARY_ACCOUNT,
    QUALITY_ISSUES,
    REASON_FOR_RETURN,
    REASON_FOR_RETURN_DESCRIPTION,
    REFUND_ACCOUNT,
    REORDER,
    REQUESTED_SLOT,
    RETURNING,
    SELECT_ORDER,
    SHIPPED,
    SHOW_MORE_COUNT,
    STOP_SHOW_MORE_COUNT,
    USER_EMAIL,
    USER_FIRST_NAME,
    USER_LAST_NAME,
    USER_OTP,
)
from dash_ecomm.database_utils import (
    get_all_orders_from_email,
    get_user_info_from_db,
    get_valid_order_count,
    get_valid_order_return,
    is_valid_otp,
    is_valid_user,
    update_order_status,
    validate_order_id,
)
from dash_ecomm.generic_utils import create_order_carousel
from rasa_sdk import Action, FormValidationAction, Tracker, events
from rasa_sdk.events import AllSlotsReset, EventType, FollowupAction, SlotSet
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

    def __get_current_orders(
        self, no_of_valid_orders: int, order_email: Text, orders: List[Dict[Text, Any]]
    ) -> (List[Dict[Text, Any]], int):
        valid_orders = []
        minimum_order_index = MIN_ITEM_IN_CAROUSEL
        maximum_order_index = MIN_ITEM_IN_CAROUSEL
        if no_of_valid_orders < MAX_ITEM_IN_CAROUSEL:
            minimum_order_index = MIN_ITEM_IN_CAROUSEL
            maximum_order_index = no_of_valid_orders
            no_of_valid_orders = STOP_SHOW_MORE_COUNT
        else:
            minimum_order_index = no_of_valid_orders - MAX_ITEM_IN_CAROUSEL
            maximum_order_index = no_of_valid_orders
            no_of_valid_orders -= MAX_ITEM_IN_CAROUSEL
        for selected_order in orders[minimum_order_index:maximum_order_index]:
            if selected_order[ORDER_COLUMN_EMAIL] == order_email and selected_order[
                ORDER_COLUMN_STATUS
            ] in [SHIPPED, RETURNING, ORDER_PENDING]:
                valid_orders.append(selected_order)
        return valid_orders, no_of_valid_orders

    def __validate_orders(
        self,
        valid_orders: List[Dict[Text, Any]],
        no_of_valid_orders: int,
        dispatcher: CollectingDispatcher,
        is_show_more_triggered: bool,
    ) -> (List[Any]):
        slot_set = []
        if not valid_orders:
            dispatcher.utter_message(template="utter_no_open_orders")
        else:
            if is_show_more_triggered:
                dispatcher.utter_message(template="utter_on_show_orders")
            else:
                dispatcher.utter_message(template="utter_open_current_orders")
            carousel_order = create_order_carousel(valid_orders)
            dispatcher.utter_message(attachment=carousel_order)
            if no_of_valid_orders > STOP_SHOW_MORE_COUNT:
                dispatcher.utter_message(template="utter_show_more_option")
                slot_set.append(
                    SlotSet(ACTION_THAT_TRIGGERED_SHOW_MORE, ACTION_ORDER_STATUS)
                )
            else:
                slot_set.append(SlotSet(ACTION_THAT_TRIGGERED_SHOW_MORE, None))
        return slot_set

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[SlotSet]:
        order_email = tracker.get_slot(USER_EMAIL)
        show_more_count = tracker.get_slot(SHOW_MORE_COUNT)
        is_show_more_triggered = tracker.get_slot(IS_SHOW_MORE_TRIGGERED)
        valid_orders = []
        no_of_valid_orders = MIN_NUMBER_ZERO
        orders = get_all_orders_from_email(order_email)
        if not is_show_more_triggered:
            no_of_valid_orders = get_valid_order_count(order_email)
        else:
            if show_more_count is None or show_more_count < MIN_NUMBER_ZERO:
                no_of_valid_orders = get_valid_order_count(order_email)
            else:
                no_of_valid_orders = show_more_count

        valid_orders, no_of_valid_orders = self.__get_current_orders(
            no_of_valid_orders, order_email, orders
        )
        slot_set = self.__validate_orders(
            valid_orders, no_of_valid_orders, dispatcher, is_show_more_triggered
        )
        slot_set.append(SlotSet(SHOW_MORE_COUNT, no_of_valid_orders))
        slot_set.append(SlotSet(IS_SHOW_MORE_TRIGGERED, False))
        return slot_set


class ShowMoreAction(Action):
    def name(self) -> Text:
        return "show_more_action"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",  # noqa: F821
    ) -> List[Dict[Text, Any]]:
        followup_action = []
        action_triggered = tracker.get_slot(ACTION_THAT_TRIGGERED_SHOW_MORE)
        if action_triggered in [
            ACTION_ORDER_STATUS,
            ACTION_RETURN_ORDER,
            ACTION_CANCEL_ORDER,
        ]:
            followup_action.append(FollowupAction(action_triggered))
            followup_action.append(SlotSet(IS_SHOW_MORE_TRIGGERED, True))
        else:
            dispatcher.utter_message(template="utter_show_more_something")
            followup_action.append(SlotSet(IS_SHOW_MORE_TRIGGERED, False))
        return followup_action


class ShowValidReturnOrders(Action):
    def name(self) -> Text:
        return "action_show_valid_return_order"

    def __create_order_carousel(
        self, delivered_orders: List[Dict[Text, Any]]
    ) -> Dict[Text, Any]:
        carousel = {
            "type": "template",
            "payload": {"template_type": "generic", "elements": []},
        }
        for selected_order in delivered_orders:
            carousel_element = {
                "title": selected_order[ORDER_COLUMN_PRODUCT_NAME],
                "subtitle": f"Status: {selected_order[ORDER_COLUMN_STATUS]}",
                "image_url": selected_order[ORDER_COLUMN_IMAGE_URL],
                "buttons": [
                    {
                        "title": SELECT_ORDER,
                        "payload": f"I want to return {selected_order[ORDER_COLUMN_ID]} order number",
                        "type": "postback",
                    },
                    {
                        "title": REORDER,
                        "payload": "",
                        "type": "postback",
                    },
                ],
            }
            carousel["payload"]["elements"].append(carousel_element)
        return carousel

    def __get_current_order(
        self,
        no_of_valid_orders: int,
        valid_orders: List[Dict[Text, Any]],
        user_mail: Text,
    ):
        carsousel_orders = []
        minimum_order_index = MIN_ITEM_IN_CAROUSEL
        maximum_order_index = MIN_ITEM_IN_CAROUSEL
        if no_of_valid_orders < MAX_ITEM_IN_CAROUSEL:
            minimum_order_index = MIN_ITEM_IN_CAROUSEL
            maximum_order_index = no_of_valid_orders
            no_of_valid_orders = STOP_SHOW_MORE_COUNT
        else:
            minimum_order_index = no_of_valid_orders - MAX_ITEM_IN_CAROUSEL
            maximum_order_index = no_of_valid_orders
            no_of_valid_orders -= MAX_ITEM_IN_CAROUSEL
        for selected_order in valid_orders[minimum_order_index:maximum_order_index]:
            carsousel_orders.append(selected_order)
        return carsousel_orders, no_of_valid_orders

    def __validate_orders(
        self,
        valid_orders: List[Dict[Text, Any]],
        no_of_valid_orders: int,
        dispatcher: CollectingDispatcher,
        is_show_more_triggered: bool,
    ) -> (List[Any]):
        slot_set = []
        if not valid_orders:
            dispatcher.utter_message(template="utter_no_open_orders")
        else:
            if is_show_more_triggered:
                dispatcher.utter_message(template="utter_orders_return_show_more")
            else:
                dispatcher.utter_message(template="utter_orders_eligible_for_return")
            carousel_order = self.__create_order_carousel(valid_orders)
            dispatcher.utter_message(attachment=carousel_order)
            if no_of_valid_orders > STOP_SHOW_MORE_COUNT:
                dispatcher.utter_message(template="utter_show_more_option")
                slot_set.append(
                    SlotSet(ACTION_THAT_TRIGGERED_SHOW_MORE, ACTION_RETURN_ORDER)
                )
            else:
                slot_set.append(SlotSet(ACTION_THAT_TRIGGERED_SHOW_MORE, None))
        return slot_set

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",  # noqa: F821
    ) -> List[Dict[Text, Any]]:
        user_mail = tracker.get_slot(USER_EMAIL)
        show_more_count = tracker.get_slot(SHOW_MORE_COUNT)
        is_show_more_triggered = tracker.get_slot(IS_SHOW_MORE_TRIGGERED)
        valid_orders = get_valid_order_return(user_mail)
        no_of_valid_orders = 0
        if not is_show_more_triggered:
            no_of_valid_orders = len(valid_orders)
        else:
            if show_more_count is None or show_more_count < MIN_NUMBER_ZERO:
                no_of_valid_orders = len(valid_orders)
            else:
                no_of_valid_orders = show_more_count
        valid_orders, no_of_valid_orders = self.__get_current_order(
            no_of_valid_orders, valid_orders, user_mail
        )
        slot_set = self.__validate_orders(
            valid_orders, no_of_valid_orders, dispatcher, is_show_more_triggered
        )
        slot_set.append(SlotSet(SHOW_MORE_COUNT, no_of_valid_orders))
        slot_set.append(SlotSet(IS_SHOW_MORE_TRIGGERED, False))
        return slot_set


class ReturnOrderAction(Action):
    def name(self) -> Text:
        return "action_return_order"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",  # noqa: F821
    ) -> List[Dict[Text, Any]]:
        order_id = tracker.get_slot(ORDER_ID_FOR_RETURN)
        update_order_status(RETURNING, order_id)
        dispatcher.utter_message(template="utter_return_initiated", order_no=order_id)
        return [
            SlotSet(ORDER_COLUMN_ID, None),
            SlotSet(REASON_FOR_RETURN, None),
            SlotSet(REASON_FOR_RETURN_DESCRIPTION),
            SlotSet(PICKUP_ADDRESS_FOR_RETURN, None),
            SlotSet(REFUND_ACCOUNT, None),
        ]


class ValidateReturnOrder(FormValidationAction):
    def name(self) -> Text:
        return "action_validate_return_order"

    def validate_order_id_for_return(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",  # noqa: F821
    ) -> List[EventType]:
        user_email = tracker.get_slot(USER_EMAIL)
        slot_set = {}
        if value is not None and validate_order_id(value, user_email):
            slot_set = {ORDER_ID_FOR_RETURN: value}
        else:
            if validate_order_id(value, user_email) is False:
                dispatcher.utter_message(template="utter_ineligible_order_id")
            else:
                dispatcher.utter_message(template="utter_ineligible_order_id")
            slot_set = {REQUESTED_SLOT: ORDER_ID_FOR_RETURN}
        return slot_set

    def validate_reason_for_return(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",  # noqa: F821
    ) -> List[EventType]:
        slot_set = {}
        if value is not None and value in [
            DONT_NEED_THE_PRODUCT,
            QUALITY_ISSUES,
            INCORRECT_ITEMS,
        ]:
            slot_set = {REASON_FOR_RETURN: value}
        else:
            dispatcher.utter_message(template="utter_invalid_reason")
            slot_set = {REQUESTED_SLOT: REASON_FOR_RETURN}
        return slot_set

    def validate_reason_for_return_description(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",  # noqa: F821
    ) -> List[EventType]:
        slot_set = {}
        if value is not None:
            slot_set = {REASON_FOR_RETURN_DESCRIPTION: value}
        else:
            slot_set = {REQUESTED_SLOT: REASON_FOR_RETURN_DESCRIPTION}
        return slot_set

    def validate_pickup_address_for_return(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",  # noqa: F821
    ) -> List[EventType]:
        slot_set = {}
        if value is not None:
            slot_set = {PICKUP_ADDRESS_FOR_RETURN: value}
        else:
            slot_set = {REQUESTED_SLOT: PICKUP_ADDRESS_FOR_RETURN}
        return slot_set

    def validate_refund_account(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",  # noqa: F821
    ) -> List[EventType]:
        slot_set = {}
        if value is not None and value in [PRIMARY_ACCOUNT, CREDIT_POINTS]:
            slot_set = {REFUND_ACCOUNT: value}
        else:
            slot_set = {REQUESTED_SLOT: REFUND_ACCOUNT}
        return slot_set
