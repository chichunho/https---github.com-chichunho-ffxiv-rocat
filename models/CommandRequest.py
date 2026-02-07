from dataclasses import dataclass
from typing import Any, Callable

import pytz
from discord.ext.commands import Context


@dataclass
class CommandRequest:
    ctx: Context
    local_tz: pytz.tzinfo
    farm: Callable
    recipe: Callable[[dict[str, Any] | list[Any] | Any], dict[str, Any]]
    args: dict[str, Any]
