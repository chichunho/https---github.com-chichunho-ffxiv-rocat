import json
import os

import aiohttp
import discord
import pytz
from discord.ext import commands
from dotenv import load_dotenv

from models.CommandRequest import CommandRequest
from universalisChef.Chef import Chef
from utils.CommandDecoder import CommandDecoder
from Waitress.GambleWaitress import GambleWaitress
from Waitress.Waitress import Waitress

load_dotenv()


class HttpSession:
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def close(self):
        await self.session.close()


class AraguBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def close(self):
        global bot_http_session
        await bot_http_session.close()
        await super().close()


intents = discord.Intents.default()
intents.message_content = True

bot = AraguBot(command_prefix=commands.when_mentioned_or("$"), intents=intents)


async def from_others(ctx: commands.Context):
    return not ctx.message.author.id == bot.user.id


@commands.check(from_others)
@bot.command(name="ping")
@bot.event
async def ping(ctx: commands.Context):
    return None
    print("pong")
    await ctx.send("pong!")


@commands.check(from_others)
@bot.command(name="info")
@bot.event
async def item_price_agg(ctx: commands.Context, item_name, q="nq"):

    return None

    global item_dict, world_dict, local_tz
    q = q.lower()

    if q not in ("hq" or "nq"):
        q = "nq"

    waitress = Waitress(world_dict, item_dict, local_tz)

    request = CommandRequest(ctx)
    request.command = "get_item_price_agg"

    item_id = 0
    try:
        if item_name in item_dict:
            item_id = int(item_dict[item_name])
    except ValueError:
        item_id = int(item_name)

    request.args = {
        "item_ids": [item_id],
        "location": "陸行鳥",
    }

    await waitress.start(request)


@commands.check(from_others)
@bot.command(name="buy")
@bot.event
async def item_price(ctx: commands.Context, args_str: str):
    global command_decoder, chef

    command_request = command_decoder.decode_command_item_price(
        ctx,
        [arg.strip() for arg in args_str.split()],
    )

    waitress = Waitress(chef)

    await waitress.start(command_request)


@commands.check(from_others)
@bot.command(name="six")
@bot.event
async def gamble_six(ctx: commands.Context, args_str: str):
    global command_decoder

    command_request = command_decoder.decode_six(
        ctx,
        [arg.strip() for arg in args_str.split()],
    )

    waitress = GambleWaitress()

    await waitress.start(command_request)


@commands.check(from_others)
@bot.command(name="alias")
@bot.event
async def alias(ctx: commands.Context, item_name, item_nickname):
    global item_dict, item_alias

    if item_name not in item_dict:
        await ctx.send(f"{item_name} is not found")

    if item_nickname not in item_dict:
        item_alias[item_nickname] = item_dict[item_name]
        item_dict[item_nickname] = item_dict[item_name]
        with open("item_alias.json", "w", encoding="utf-8") as out_f:
            json.dump(item_alias, out_f)
        await ctx.send(f"{item_nickname} is now an alias of item {item_name}")
    else:
        await ctx.send(f"{item_nickname} is an alias of item {item_dict[item_nickname]}")


@bot.event
async def on_ready():
    global item_dict
    item_dict = {}
    with open("Item.json", "r", encoding="utf-8") as in_f:
        _item_dict: dict[str, str] = json.load(in_f)
    for item_id, item_name in _item_dict.items():
        item_dict[item_id] = item_name
        item_dict[item_name] = item_id
    del _item_dict

    global item_alias
    item_alias = {}
    with open("item_alias.json", "r", encoding="utf-8") as in_f:
        item_alias = json.load(in_f)

    for item_nickname, item_id in item_alias.items():
        item_dict[item_nickname] = item_id

    global world_dict
    world_dict = {}
    with open("worlds.json", "r", encoding="utf-8") as in_f:
        world_dict = json.load(in_f)

    global local_tz
    local_tz = pytz.timezone("Asia/Taipei")

    global bot_http_session
    bot_http_session = HttpSession()

    global command_decoder
    command_decoder = CommandDecoder(item_dict, world_dict, local_tz, bot_http_session)

    global chef
    chef = Chef(world_dict, item_dict, local_tz)


if __name__ == "__main__":
    bot.run(os.getenv("BOT_TOKEN"))
