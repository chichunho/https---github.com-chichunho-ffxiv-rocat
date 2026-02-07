from datetime import datetime
from typing import Any, Callable

import pytz

from universalisChef.recipe import ItemPrice, ItemPriceAgg


class Chef:
    def __init__(
        self,
        world_dict: dict[str, str],
        item_dict: dict[str, str],
        local_tz: pytz.tzinfo,
    ):
        self.world_dict = world_dict
        self.item_dict = item_dict
        self.local_tz = local_tz

    def cook(self, veggie: dict[str, Any] | list[Any] | Any, recipe: Callable):
        pre_soup = recipe(veggie)
        if isinstance(recipe, ItemPrice):
            self._cook_item_price(pre_soup)
        return pre_soup

    def _cook_item_price(self, pre_soup: Any):
        pre_soup["name"] = self.item_dict[str(pre_soup["name"])]

        pre_soup["update_time"] = (
            datetime.fromtimestamp(pre_soup["update_time"] // 1000)
            .astimezone(self.local_tz)
            .strftime("%Y-%m-%d %H:%M")
        )

        # for world_stat in pre_soup["world_stats"].values():
        #     for q in ["nq", "hq"]:
        #         for t in ["min_per_unit", "min_total"]:
        #             if world_stat[q][t]["count"] >= 100:
        #                 world_stat[q][t]["count"] = "99+"
        #             else:
        #                 world_stat[q][t]["count"] = str(world_stat[q]["count"])

        pre_soup["world_stats"] = {
            k: v
            for k, v in sorted(
                pre_soup["world_stats"].items(), key=lambda x: x[1]["nq"]["min_per_unit"]["price"]
            )
        }
        pre_soup["world_stats"] = {
            k: v
            for k, v in sorted(
                pre_soup["world_stats"].items(), key=lambda x: x[1]["hq"]["min_per_unit"]["price"]
            )
        }

    def cook_item_price_agg(self, data: Any):
        """
        data exmaple with data center provided
        {
            "results": [
                {
                "itemId": 32949,
                "nq": {
                    "minListing": {
                    "dc": { "price": 300, "worldId": 4029 },
                    "region": { "price": 300, "worldId": 4029 }
                    },
                    "recentPurchase": {
                    "dc": { "price": 400, "timestamp": 1769788028000, "worldId": 4030 },
                    "region": { "price": 400, "timestamp": 1769788028000, "worldId": 4030 }
                    },
                    "averageSalePrice": {
                    "dc": { "price": 300.7365439093484 },
                    "region": { "price": 300.7365439093484 }
                    },
                    "dailySaleVelocity": {
                    "dc": { "quantity": 115.00055049673288 },
                    "region": { "quantity": 115.00054997664657 }
                    }
                },
                "hq": {
                    "minListing": {},
                    "recentPurchase": {},
                    "averageSalePrice": {},
                    "dailySaleVelocity": {}
                },
                "worldUploadTimes": [ { "worldId": 4029, "timestamp": 1769782436783 } ]
                }
            ],
            "failedItems": []
        }
        """
        data_row = data["results"][0] if len(data["results"]) > 0 else None
        if data_row is None:
            return None
        soup = ItemPriceAgg(data_row, self.world_dict, self.item_dict, self.local_tz).soup
        return soup
