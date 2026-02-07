from models.CommandRequest import CommandRequest
from universalisChef.Chef import Chef
from utils.Embed import ItemPriceEmbed


class Waitress:
    def __init__(self, chef: Chef):
        self.chef = chef

    async def start(self, request: CommandRequest):
        if request.args["item_ids"] is None:
            await request.ctx.message.reply(content="物品不存在, 請確認物品名稱")
            return
        veggie = await request.farm(**request.args)

        soup = self.chef.cook(veggie, request.recipe)

        await request.ctx.message.reply(embed=ItemPriceEmbed(soup).message())
