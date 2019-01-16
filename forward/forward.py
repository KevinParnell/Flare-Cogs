from redbot.core import commands
import discord


class Forward(commands.Cog):
    """Forward messages to the bot to the bot owner."""

    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        owner = self.bot.get_user(self.bot.owner_id)
        if message.guild != None:
            return
        if message.channel.recipient.id == self.bot.owner_id:
            return
        if message.author == self.bot.user:
            embed = discord.Embed(title=f"Sent PM to {message.channel.recipient}({message.channel.recipient.id}).",
                                  timestamp=message.created_at)
            await owner.send(embed=embed)
        else:
            if message.content[0] not in await self.bot.get_prefix(message):
                embed = discord.Embed(description=message.content, timestamp=message.created_at)
                embed.set_author(name=message.author, icon_url=message.author.avatar_url)
                await owner.send(embed=embed)
