import datetime
import re
from datetime import datetime, timedelta  # noqa:  F811
from typing import Any, Dict, List, Text

from dash_ecomm.constants import (
    CANCEL_ORDER,
    ORDER_COLUMN_IMAGE_URL,
    ORDER_COLUMN_PRODUCT_NAME,
    ORDER_COLUMN_STATUS,
    ORDER_PENDING,
    PRODUCT_DETAILS,
    RETURNING,
    SHIPPED,
    ORDER_STATUS,
)


def get_unblock_timestamp(after_n_minutes: int = 2) -> datetime:
    now = datetime.now()
    delta = timedelta(minutes=after_n_minutes)
    unblock_timestamp = now + delta
    return unblock_timestamp


def add_track_item_button(
    order: Dict[Text, Any], carousel: Dict[Text, Any]
) -> Dict[Text, Any]:
    if order[ORDER_COLUMN_STATUS] in [SHIPPED, RETURNING, ORDER_PENDING]:
        carousel["buttons"].append(
            {"title": ORDER_STATUS, "payload": "", "type": "postback"}
        )


def create_order_carousel(orders: List[Dict[Text, Any]]) -> Dict[Text, Any]:
    carousel = {
        "type": "template",
        "payload": {"template_type": "generic", "elements": []},
    }
    for selected_order in orders:
        carousel_element = {
            "title": selected_order[ORDER_COLUMN_PRODUCT_NAME],
            "subtitle": f"Status: {selected_order[ORDER_COLUMN_STATUS]}",
            "image_url": selected_order[ORDER_COLUMN_IMAGE_URL],
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
        add_track_item_button(selected_order, carousel_element)
        carousel["payload"]["elements"].append(carousel_element)
    return carousel


def is_valid_order_id(order_id: Text) -> bool:
    order_id_regex = "^DASH[0-9]{6}$"
    compiled_regex = re.compile(order_id_regex)
    if re.search(compiled_regex, order_id):
        return True
    else:
        return False
