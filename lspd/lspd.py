from redbot.core import commands, Config

from redbot.core.utils.chat_formatting import pagify
import discord
import random
from prettytable import PrettyTable

defaults_guild = {"apbs": {}, "users": {}, "times": {}}


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
                    if destination in ctx.message.guild.members:
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

    @commands.command(aliases=["times"])
    async def time(self, ctx, *, crimes: str):
        """Max jail time program"""
        crimes = crimes.split(",")
        fail = []
        async with self.config.guild(ctx.guild).times() as time:
            totaltime = 0
            for crime in crimes:
                crime = crime.lower().lstrip()
                if crime in time:
                    totaltime += time[crime]
                else:
                    fail.append(crime.lstrip())
        if totaltime <= 60:
            await ctx.send(f"The maximum time would be {totaltime} minutes.")
        else:
            await ctx.send(f"The maximum time would be {totaltime} minutes however WC-RP forces a 60 minutes max rule.")
        if fail:
            await ctx.send("The following crimes were not recognized:\n" + "\n".join(fail))

    @commands.command(aliases=["addtimes"])
    async def addtime(self, ctx, time: int, *, crime: str):
        """Add a time to the database"""
        supervisors = []
        for member in ctx.guild.members:
            if member.top_role.name == "High Command":
                supervisors.append(member.id)
            if member.top_role.name == "Command":
                supervisors.append(member.id)
        if ctx.author.id not in supervisors:
            return
        async with self.config.guild(ctx.guild).times() as times:
            times[crime.lower()] = time
            await ctx.send(f"The crime {crime} with a max time of {time} has been added to the system.")

    @commands.command()
    async def listtimes(self, ctx):
        """List times for the current guild."""
        async with self.config.guild(ctx.guild).times() as times:
            t = PrettyTable(["Crime", "Time"])
            for crime in times:
                t.add_row([crime.title(), times[crime]])

            for page in pagify(str(t)):
                await ctx.send("```py\n{}\n".format(str(page) + "```"))

    @commands.command()
    async def deltime(self, ctx, *, crime: str):
        """Delete a time"""
        crime = crime.lower()
        supervisors = []
        for member in ctx.guild.members:
            if member.top_role.name == "High Command":
                supervisors.append(member.id)
            if member.top_role.name == "Command":
                supervisors.append(member.id)
        if ctx.author.id not in supervisors:
            return
        async with self.config.guild(ctx.guild).times() as times:
            if crime in times:
                del times[crime]
                await ctx.send(f"{crime.title()} has been removed from the time list.")
            else:
                await ctx.send(f"{crime.title()} was not found in the current time list.")
