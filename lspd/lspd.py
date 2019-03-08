from redbot.core import commands, Config
import discord
import random

defaults_guild = {"apbs": {}, "users": {}}


class LSPD(commands.Cog):
    """WC-RP LSPD"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=146130471346, force_registration=True)
        self.config.register_guild(**defaults_guild)

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

        async with self.config.guild(ctx.guild).apbs() as apb:
            key = name.content
            apb[key] = {"name": name.content, "reason": crimes.content, "officer": ctx.author.display_name,
                        "creator": ctx.author.id}
        await ctx.send("APB Added Successfully.")

        async with self.config.guild(ctx.guild).users() as users:
            for user in users:
                if users[user]:
                    destination = self.bot.get_user(int(user))
                    await destination.send(
                        "A new APB has been posted!\n---------------\nSuspect: {}\nReason: {}\nAPB Issued By: {}".format(
                            name.content, crimes.content, ctx.author.display_name))

    @apb.command()
    async def delete(self, ctx, *, name: str):
        """Remove an APB"""
        supervisors = []
        for member in ctx.guild.members:
            if member.top_role.name == "High Command":
                supervisors.append(member.id)
            elif member.top_role.name == "Command":
                supervisors.append(member.id)
            elif member.top_role.name == "Supervisors":
                supervisors.append(member.id)
        async with self.config.guild(ctx.guild).apbs() as apb:
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
        async with self.config.guild(ctx.guild).apbs() as data:
            colour = discord.Color.from_hsv(random.random(), 1, 1)
            embed = discord.Embed(
                title="Current APBs", colour=colour)
            for name in data:
                if len(data[name]['name']) > 20:
                    embed.add_field(name="Reason:", value=f"{data[name]['name'][:20]}...", inline=True)
                else:
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
        async with self.config.guild(ctx.guild).apbs() as apbs:
            if name not in apbs:
                await ctx.send("User doesn't have an active APB.")
                return
            await ctx.send(
                "APB Information for {}:\nReason: {}\nIssued by: {}".format(name, apbs[name]['reason'],
                                                                            apbs[name]['officer']))

    @apb.command()
    async def notify(self, ctx, status: bool):
        """Enable DM notifications for new APBs"""
        async with self.config.guild(ctx.guild).users() as users:
            key = str(ctx.author.id)
            users[key] = status
            if status:
                await ctx.send("You've enabled DM notifications for new APBs.")
            else:
                await ctx.send("You've disabled DM notifications for new APBs.")
