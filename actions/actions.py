from typing import Any, Dict, List, Text

import yaml
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

# change this to the location of your SQLite file
path_to_db = "actions/example1.yml"


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
        database = open(r"actions/example1.yml")
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
        database = open(r"actions/example1.yml")
        orders = yaml.load(database, Loader=yaml.FullLoader)

        # get email slot
        order_email = (tracker.get_slot("email"),)

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
        database = open("actions/example1.yml", "r")
        orders = yaml.load(database, Loader=yaml.FullLoader)

        # get email slot
        order_email = (tracker.get_slot("email"),)

        # retrieve row based on email
        for order in orders["orders"]:
            if order["order_email"] == order_email:
                orderStatus = order["status"]
                break

        if orderStatus != "":
            # change status of entry
            status = [("cancelled"), (tracker.get_slot("email"))]
            orderStatus = status[0]
            for order in orders["orders"]:
                if order["email"] == order_email:
                    order["status"] = orderStatus
            write = open("example1.yml", "w")
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
        database = open(r"actions/example1.yml")
        orders = yaml.load(database, Loader=yaml.FullLoader)

        # get email slot
        order_email = (tracker.get_slot("email"),)

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
            write = open("example1.yml", "w")
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
