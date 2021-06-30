# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Tuple
import logging
from rasa_sdk import Action, Tracker,events, FormValidationAction
from rasa_sdk.events import (
    ActiveLoop,
    AllSlotsReset,
    EventType,
    FollowupAction,
    SlotSet,
)
from rasa_sdk.executor import CollectingDispatcher
from doc_guru.database_utils import give_step, give_current_step, update_step_value, is_valid_user, is_valid_otp, get_user_info_from_db
from doc_guru.generic_utils import get_unblock_timestamp
logger = logging.getLogger(__name__)

class action_utter_setup(Action):
    def name(self) -> Text:
        return "action_utter_setup"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        service = 'ec2'
        buttons = [{"title": "Completed", "payload": "/next_step"}]
        if service:
            step_value = give_current_step(user='prakashr7d@gmail.com', service=service)
            message = give_step(step=step_value, service=service)
            if message:
                dispatcher.utter_message(message, buttons=buttons)
                step_value = int(step_value) + 1
                update_step_value('prakashr7d@gmail.com', service, str(step_value))

        return []

class LoginFormAction(Action):
    def name(self) -> Text:
        return "action_login_form"

    def __set_unblock_reminder(self, tracker: Tracker):
        set_reminder = True if tracker.get_slot("email_tries") > 0 else False

        reminder_events = []
        if set_reminder:
            logger.debug("*" * 100)
            logger.debug(set_reminder)
            timestamp = get_unblock_timestamp()
            login_event = events.ReminderScheduled(
                intent_name="EXTERNAL_unblock_login",
                trigger_date_time=timestamp,
                name="login_unblock",
                kill_on_user_message=False,
            )
            reminder_events.append(login_event)
        return reminder_events

    @staticmethod
    def validate_user(useremail: Text):
        user_profile = None
        if is_valid_user(useremail):
            user_profile = get_user_info_from_db(useremail)
        return user_profile

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
        login_blocked = tracker.get_slot('login_blocked')
        slot_set = []
        if login_blocked:
            dispatcher.utter_message(template="utter_login_blocked")
            dispatcher.utter_message(template="utter_login_blocked_duration")
            dispatcher.utter_message(template="utter_login_via_website")

            reminder_events = self.__set_unblock_reminder(tracker)
            slot_set += [SlotSet("email_tries", 0), SlotSet('otp_tries', 0)]
            slot_set += reminder_events
        else:
            user_email = tracker.get_slot("user_email")
            user_profile = self.validate_user(user_email)
            if user_profile and not tracker.get_slot('is_logged_in'):
                dispatcher.utter_message(template="utter_login_success")
                slot_set += [
                    SlotSet(key="user_email", value=user_profile.email),
                    SlotSet(key="user_first_name", value=user_profile.first_name),
                    SlotSet(key='user_last_name', value=user_profile.last_name),
                    SlotSet(key='is_logged_in', value=True),
                    SlotSet(key='user_otp', value=user_profile.otp),
                ]
            elif user_profile and tracker.get_slot('is_logged_in'):
                pass
            else:
                dispatcher.utter_message(template="utter_login_failed")
        logger.debug(slot_set)
        return slot_set

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
        return [SlotSet('login_blocked', False)]


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
class ValidateLoginForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_login_form"

    def __utter_message_and_slots(
        self, email: Text, slots: Dict[Text, Text]
    ) -> Tuple[Text, Dict]:
        slots = slots if slots else {}
        slots['user_email'] = None
        if email is None:
            utter = "utter_email_not_valid_prompt"
        elif not is_valid_user(email):
            utter = "utter_user_email_not_registered"
            slots['requested_slot'] = None
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
        email_tries = tracker.get_slot('email_tries')
        returned_slots = {}
        if value is not None and is_valid_user(value):
            returned_slots = {'user_email': value}
        elif email_tries >= 2:
            returned_slots = {
                'requested_slot': None,
                'login_blocked': True,
                'user_email': None,
            }
        else:
            email_tries += 1
            utter, returned_slots = self.__utter_message_and_slots(
                value, returned_slots
            )
            logger.debug(returned_slots)
            dispatcher.utter_message(template=utter)
            returned_slots['email_tries'] = email_tries
        return returned_slots

    def validate_user_otp(
        self,
        value: Text,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",  # noqa: F821
    ) -> List[EventType]:
        email = tracker.get_slot('user_email')
        otp_tries = tracker.get_slot('otp_tries')
        if value is not None and is_valid_otp(value, email):
            logger.debug(f"{value} is a valid user")
            returned_slots = {'user_otp': value}
        else:
            if otp_tries >= 2:
                returned_slots = {
                    'requested_slot': None,
                    'login_blocked': True,
                    'user_otp': None,
                }
            else:
                otp_tries += 1
                dispatcher.utter_message(template="utter_incorrect_otp")
                returned_slots = {'user_otp': None, 'otp_tries': otp_tries}
        return returned_slots

    class ValidateLoginForm(FormValidationAction):
        def name(self) -> Text:
            return "validate_login_form"

        def __utter_message_and_slots(
                self, email: Text, slots: Dict[Text, Text]
        ) -> Tuple[Text, Dict]:
            slots = slots if slots else {}
            slots['user_email'] = None
            if email is None:
                utter = "utter_email_not_valid_prompt"
            elif not is_valid_user(email):
                utter = "utter_user_email_not_registered"
                slots['requested_slot'] = None
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
            email_tries = tracker.get_slot('email_tries')
            returned_slots = {}
            if value is not None and is_valid_user(value):
                returned_slots = {'user_email': value}
            elif email_tries >= 2:
                returned_slots = {
                    'requested_slot': None,
                    'login_blocked': True,
                    'user_email': None,
                }
            else:
                email_tries += 1
                utter, returned_slots = self.__utter_message_and_slots(
                    value, returned_slots
                )
                logger.debug(returned_slots)
                dispatcher.utter_message(template=utter)
                returned_slots['email_tries'] = email_tries
            return returned_slots

        def validate_user_otp(
                self,
                value: Text,
                dispatcher: "CollectingDispatcher",
                tracker: "Tracker",
                domain: "DomainDict",  # noqa: F821
        ) -> List[EventType]:
            email = tracker.get_slot('user_email')
            otp_tries = tracker.get_slot('otp_tries')
            if value is not None and is_valid_otp(value, email):
                logger.debug(f"{value} is a valid user")
                returned_slots = {'user_otp': value}
            else:
                if otp_tries >= 2:
                    returned_slots = {
                        'requested_slot': None,
                        'login_blocked': True,
                        'user_otp': None,
                    }
                else:
                    otp_tries += 1
                    dispatcher.utter_message(template="utter_incorrect_otp")
                    returned_slots = {'user_otp': None, 'otp_tries': otp_tries}
            return returned_slots

class ActionnAllSlotReset(Action):
    def name(self) -> Text:
        return "action_all_slot_reset"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",  # noqa: F821
    ) -> List[Dict[Text, Any]]:

        return [AllSlotsReset()]