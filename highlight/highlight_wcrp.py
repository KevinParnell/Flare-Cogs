from redbot.core import commands, Config, checks


class Highlight(commands.Cog):
    """Forward messages to a set channel."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1398467138476, force_registration=True)
        default_global = {"highlight": {}, "toggle": {"status": True}}
        self.config.register_global(**default_global)

    async def on_message(self, message):
        channels = [461965008536862720]
        if message.channel.id in channels:
            async with self.config.highlight() as highlight:
                for user in highlight:
                    if highlight[user].lower() in message.content.lower():
                        if highlight[user].lower() in message.content.split(":", 1)[0].lower():
                            return
                        highlighted = self.bot.get_user(int(user))
                        await highlighted.send(
                            "You've been mentioned in {}.\nContext: {}".format(message.channel.name, message.content))

    @commands.has_any_role("Management", "Senior Administrator", "Lead Administrator", "Administrator",
                           "Moderator", "Server Manager")
    @commands.command()
    async def highlight(self, ctx, *, text: str):
        """Add a word to be highlighted on."""
        async with self.config.highlight() as highlight:
            highlight[f"{ctx.author.id}"] = text
            await ctx.send("Done.")
