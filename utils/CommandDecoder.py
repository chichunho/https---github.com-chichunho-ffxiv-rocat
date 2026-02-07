from typing import Any

import pytz
from discord.ext.commands import Context

from models.CommandRequest import CommandRequest
from universalis.Client import Client
from universalisChef.recipe import ItemPrice


class CommandDecoder:
    def __init__(
        self,
        item_dict: dict[str, str],
        world_dict: dict[str, str],
        local_tz: pytz.tzinfo,
        http_session: Any,
    ):
        self.item_dict = item_dict
        self.world_dict = world_dict
        self.local_tz = local_tz
        self.http_session = http_session
        self.recipe = None
        self.args = {}

    def decode_command_item_price(self, ctx: Context, args: list[str]):
        item_name = args[0]
        hq = args[1] if len(args) > 1 else None
        #  location = args[2] if len(args) > 2 else "陸行鳥"

        item_id = None
        try:
            if item_name in self.item_dict:
                item_id = int(self.item_dict[item_name])
        except ValueError:
            item_id = int(item_name)

        if hq is not None:
            hq = True if hq.lower() == "hq" else False

        args = {
            "item_ids": [item_id] if item_id is not None else None,
            "location": "陸行鳥",
            "hq": hq,
            "listings": None,
            "sale_entries": 0,
            "stats_within": None,
            "sale_entries_within": None,
            "fields": [
                "itemID",
                "lastUploadTime",
                "listings.pricePerUnit",
                "listings.quantity",
                "listings.worldName",
                "listings.hq",
                "listings.total",
                "listings.tax",
                "currentAveragePriceNQ",
                "currentAveragePriceHQ",
                "minPriceNQ",
                "minPriceHQ",
                "listingsCount",
                "unitsForSale",
            ],
        }

        return CommandRequest(
            ctx,
            self.local_tz,
            Client(self.http_session).get_item_price,
            ItemPrice(),
            args,
        )

    def decode_six(self, ctx: Context, args: list[str]):
        args = {
            "input_map": args[0],
            "global_cand": [i for i in range(1, 10) if str(i) not in args[0]],
        }

        return CommandRequest(
            ctx,
            None,
            None,
            None,
            args,
        )
