import discord
from redbot.core import commands, checks
from random import randint
import aiohttp
import asyncio

BaseCog = getattr(commands, "Cog", object)


class Foco(BaseCog):
    """WC-RP's Commands"""

    def __init__(self, bot):
        self.bot = bot
        self._session = aiohttp.ClientSession()

    async def __unload(self):
        asyncio.get_event_loop().create_task(self._session.close())

    async def get(self, url):
        async with self._session.get(url) as response:
            return await response.json()

    async def on_member_update(self, before, after):
        channel = self.bot.get_channel(549707840328302603)
        request = "https://api.samp-servers.net/v2/server/185.107.96.114:7779"
        req = await self.get(request)
        players = int(f"{req['core']['pc']}")
        if players < 10:
            u10 = str(channel.name[17:18])
        else:
            u10 = str(channel.name[17:19])
        if u10 != str(players):
            playerss = f"Current Players: {players}/400"
            await channel.edit(name=f"{playerss}")

    @commands.command(
        pass_context=True,
        aliases=[
            "serverip",
            "ips",
            "foco",
            "ftdm",
            "site",
            "website",
            "forum",
            "forums",
        ],
    )
    async def ip(self, ctx):
        """FoCo's server IP."""

        colour = randint(0, 0xFFFFFF)
        embed = discord.Embed(title="FoCo TDM", colour=discord.Colour(value=colour))
        embed.add_field(name="IP", value="N/A", inline=True)
        embed.add_field(name="Numerical IP", value="N/A", inline=True)
        embed.add_field(name="SA-MP Version", value="0.3DL", inline=True)
        embed.add_field(name="Forums", value="N/A", inline=True)
        embed.add_field(name="Discord Invite Link", value="N/A", inline=True)
        embed.add_field(name="Server Version", value="3.8.7", inline=True)
        embed.set_footer(text="N/A ")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def rules(self, ctx):
        """FoCo's server rules."""

        embed = discord.Embed(
            title="FoCoTDM Rules",
            colour=0xFF6A14,
            description="**FoCo Team Deathmatch Brief**\n\nThe Carnage Clan is proud to announce the revival of the revolutionary and notorious TDM server initially founded by Shaney and Wazza in 2011, **FoCo TDM**.",
        )
        embed.add_field(
            name="**Information**",
            value="Welcome to the Discord server of **FoCo TDM**!\nPlease make sure that you've read the rules before joining!",
        )
        embed.add_field(
            name="Rules",
            value="1. Don't be disrespectful towards the other members of the community. We know, a joke is a joke but don't take it too far.\n2. Keep discussions to relevant text channels.\n3. Don't scream / play annoying distorted audio clips in voice channels.\n4. Promotion of other Discord servers or SA:MP servers is strictly forbidden.\n5. No spamming.\n6. English only.\n\n\nIf you see anyone breaking these rules, please take a screenshot and send it to a **Server Administrator**",
            inline=True,
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def status(self, ctx):
        r = "https://api.samp-servers.net/v2/server/185.107.96.114:7779"
        req = await self.get(r)
        players = f"{req['core']['pc']}/{req['core']['pm']}"
        ip = req["core"]["ip"]
        online = req["active"]
        if online:
            await ctx.send(
                "**FoCo TDM Status:**\n\n:desktop: IP: {}\n:white_check_mark: Status: **Online**\n:video_game: Players: {}".format(
                    ip, players
                )
            )
        else:
            await ctx.send("FoCo TDM is currently offline.")
