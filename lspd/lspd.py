from redbot.core import commands, Config
import discord
import random

defaults_global = {"apbs": {}}


class LSPD(commands.Cog):
    """WC-RP LSPD"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=146130471346, force_registration=True)
        self.config.register_global(**defaults_global)

    @commands.group(autohelp=True)
    async def apb(self, ctx):
        """WC-RP APB Commands"""
        pass

    @apb.command()
    async def add(self, ctx):
        """Add an APB"""
        await ctx.send("Please enter the suspects name")
        name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        await ctx.send(f"The suspect you have entered is: {name.content}\nPlease now enter the reason for this APB.")
        crimes = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        await ctx.send(f"Reason added successfully, please enter your name now.")
        officer = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        async with self.config.apbs() as apb:
            key = name.content
            apb[key] = {"name": name.content, "reason": crimes.content, "officer": officer.content,
                        "creator": ctx.author.id}
        await ctx.send("APB Added Successfully.")

    @apb.command()
    async def delete(self, ctx, *, name: str):
        """Remove an APB"""
        supervisors = [334409039486255105, 334408515076620291, 219112945416667138, 95932766180343808,
                       169162432739016704, 138526015646466048, 261597186977038337, 307496008189870090,
                       173781562951860224]
        async with self.config.apbs() as apb:
            if name not in apb:
                await ctx.send("User doesn't have an active APB.")
                return
            if ctx.author.id == apb[f'{name}']['creator'] or ctx.author.id in supervisors:
                del apb[f'{name}']
                await ctx.send("APB removed.")
            else:
                await ctx.send("You don't have permission to remove this APB.")

    @apb.command()
    async def list(self, ctx):
        """List all active APBs"""
        async with self.config.apbs() as data:
            colour = discord.Color.from_hsv(random.random(), 1, 1)
            embed = discord.Embed(
                title="Current APBs", colour=colour)
            for name in data:
                embed.add_field(name="Suspect:", value=data[name]['name'], inline=True)
                if len(data[name]['reason']) > 20:
                    embed.add_field(name="Reason:", value=f"{data[name]['reason'][:20]}...", inline=True)
                else:
                    embed.add_field(name="Reason:", value=data[name]['reason'], inline=True)
                if len(data[name]['officer']) > 20:
                    embed.add_field(name="Reason:", value=f"{data[name]['officer'][:20]}...", inline=True)
                else:
                    embed.add_field(name="Officer:", value=data[name]['officer'], inline=True)
            await ctx.send(embed=embed)

    @apb.command()
    async def info(self, ctx, *, name: str):
        """List info on a current suspect."""
        async with self.config.apbs() as apbs:
            if name not in apbs:
                await ctx.send("User doesn't have an active APB.")
                return
            await ctx.send(
                "APB Information for {}:\nReason: {}\nIssued by: {}".format(name, apbs[name]['reason'],
                                                                            apbs[name]['officer']))
