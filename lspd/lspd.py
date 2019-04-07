from redbot.core import commands, Config, checks
from redbot.core.utils.chat_formatting import pagify
import discord
import random
import typing

from prettytable import PrettyTable

defaults_guild = {"apbs": {}, "users": {}, "times": {}, "tickets": {}}


class LSPD(commands.Cog):
    """VCPD"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=146130471346, force_registration=True)
        self.config.register_guild(**defaults_guild)

    @commands.group(autohelp=True)
    async def apb(self, ctx):
        """APB Commands"""
        pass

    @apb.command()
    async def add(self, ctx):
        """Add an APB"""
        await ctx.send("Please enter the suspects name")
        name = await self.bot.wait_for(
            "message", check=lambda message: message.author == ctx.author
        )
        await ctx.send(
            f"The suspect you have entered is: {name.content}\nPlease now enter the reason for this APB."
        )
        crimes = await self.bot.wait_for(
            "message", check=lambda message: message.author == ctx.author
        )

        async with self.config.guild(ctx.guild).apbs() as apb:
            key = name.content
            apb[key] = {
                "name": name.content,
                "reason": crimes.content,
                "officer": ctx.author.display_name,
                "creator": ctx.author.id,
            }
        await ctx.send("APB Added Successfully.")

        async with self.config.guild(ctx.guild).users() as users:
            for user in users:
                if users[user]:
                    destination = self.bot.get_user(int(user))
                    if destination in ctx.message.guild.members:
                        await destination.send(
                            "A new APB has been posted!\n---------------\nSuspect: {}\nReason: {}\nAPB Issued By: {}".format(
                                name.content, crimes.content, ctx.author.display_name
                            )
                        )

    @apb.command()
    async def delete(self, ctx, *, name: str):
        """Remove an APB"""
        supervisors = []
        for member in ctx.guild.members:
            if member.top_role.name == "Executive Staff":
                supervisors.append(member.id)
            elif member.top_role.name == "Command Staff":
                supervisors.append(member.id)
            elif member.top_role.name == "Supervisory Staff":
                supervisors.append(member.id)
        async with self.config.guild(ctx.guild).apbs() as apb:
            if name not in apb:
                await ctx.send("User doesn't have an active APB.")
                return
            if ctx.author.id == apb[f"{name}"]["creator"] or ctx.author.id in supervisors:
                del apb[f"{name}"]
                await ctx.send("APB removed.")
            else:
                await ctx.send("You don't have permission to remove this APB.")

    @apb.command()
    async def list(self, ctx):
        """List all active APBs"""
        async with self.config.guild(ctx.guild).apbs() as data:
            colour = discord.Color.from_hsv(random.random(), 1, 1)
            embed = discord.Embed(title="Current APBs", colour=colour)
            for name in data:
                if len(data[name]["name"]) > 20:
                    embed.add_field(
                        name="Reason:", value=f"{data[name]['name'][:20]}...", inline=True
                    )
                else:
                    embed.add_field(name="Suspect:", value=data[name]["name"], inline=True)
                if len(data[name]["reason"]) > 20:
                    embed.add_field(
                        name="Reason:", value=f"{data[name]['reason'][:20]}...", inline=True
                    )
                else:
                    embed.add_field(name="Reason:", value=data[name]["reason"], inline=True)
                if len(data[name]["officer"]) > 20:
                    embed.add_field(
                        name="Reason:", value=f"{data[name]['officer'][:20]}...", inline=True
                    )
                else:
                    embed.add_field(name="Officer:", value=data[name]["officer"], inline=True)
            await ctx.send(embed=embed)

    @apb.command()
    async def info(self, ctx, *, name: str):
        """List info on a current suspect."""
        async with self.config.guild(ctx.guild).apbs() as apbs:
            if name not in apbs:
                await ctx.send("User doesn't have an active APB.")
                return
            await ctx.send(
                "APB Information for {}:\nReason: {}\nIssued by: {}".format(
                    name, apbs[name]["reason"], apbs[name]["officer"]
                )
            )

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
        """Penal Code Calculator - seperate multiple crimes with ,
           Example - [p]time murder, evasion, GTA"""
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
        await ctx.send(f"The maximum time would be {totaltime} minutes.")
        if fail:
            await ctx.send("The following crimes were not recognized:\n" + "\n".join(fail))

    @commands.command(aliases=["addtimes"])
    async def addtime(self, ctx, time: int, *, crime: str):
        """Add a time to the database - Command Staff +"""
        supervisors = []
        for member in ctx.guild.members:
            if member.top_role.name == "Executive Staff":
                supervisors.append(member.id)
            if member.top_role.name == "Command Staff":
                supervisors.append(member.id)
        if ctx.author.id not in supervisors:
            return
        async with self.config.guild(ctx.guild).times() as times:
            times[crime.lower()] = time
            await ctx.send(
                f"The crime {crime} with a max time of {time} has been added to the system."
            )

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
        """Delete a timetimes - Command Staff +"""
        crime = crime.lower()
        supervisors = []
        for member in ctx.guild.members:
            if member.top_role.name == "Executive Staff":
                supervisors.append(member.id)
            if member.top_role.name == "Command Staff":
                supervisors.append(member.id)
        if ctx.author.id not in supervisors:
            return
        async with self.config.guild(ctx.guild).times() as times:
            if crime in times:
                del times[crime]
                await ctx.send(f"{crime.title()} has been removed from the time list.")
            else:
                await ctx.send(f"{crime.title()} was not found in the current time list.")

    @commands.command()
    async def price(self, ctx, *, tickets: str):
        """TicketCalculator - seperate multiple crimes with ,"""
        tickets = tickets.split(",")
        fail = []
        async with self.config.guild(ctx.guild).tickets() as ticketprices:
            totaltime = 0
            for ticket in tickets:
                ticket = ticket.lower().lstrip()
                if ticket in ticketprices:
                    totaltime += ticketprices[ticket]
                else:
                    fail.append(ticket.lstrip())
        await ctx.send(f"The maximum price would be ${totaltime}.")
        if fail:
            await ctx.send("The following tickets were not recognized:\n" + "\n".join(fail))

    @commands.command()
    async def addticket(self, ctx, price: int, *, ticket: str):
        """Add a ticket to the database - Command Staff +"""
        supervisors = []
        for member in ctx.guild.members:
            if member.top_role.name == "Executive Staff":
                supervisors.append(member.id)
            if member.top_role.name == "Command Staff":
                supervisors.append(member.id)
        if ctx.author.id not in supervisors:
            return
        async with self.config.guild(ctx.guild).tickets() as tickets:
            tickets[ticket.lower()] = price
            await ctx.send(
                f"The ticket {ticket} with a max price of {price} has been added to the system."
            )

    @commands.command()
    async def delticket(self, ctx, *, ticket: str):
        """Delete a ticket - Command Staff +"""
        ticket = ticket.lower()
        supervisors = []
        for member in ctx.guild.members:
            if member.top_role.name == "Executive Staff":
                supervisors.append(member.id)
            if member.top_role.name == "Command Staff":
                supervisors.append(member.id)
        if ctx.author.id not in supervisors:
            return
        async with self.config.guild(ctx.guild).tickets() as tickets:
            if ticket in tickets:
                del tickets[ticket]
                await ctx.send(f"{ticket.title()} has been removed from the price list.")
            else:
                await ctx.send(f"{ticket.title()} was not found in the current price list.")

    @commands.command()
    async def listtickets(self, ctx):
        """List tickets for the current guild."""
        async with self.config.guild(ctx.guild).tickets() as tickets:
            t = PrettyTable(["Tickets", "Price"])
            for ticket in tickets:
                t.add_row([ticket.title(), tickets[ticket]])

            for page in pagify(str(t)):
                await ctx.send("```py\n{}\n".format(str(page) + "```"))

    @checks.is_owner()
    @commands.command()
    async def convert(self, ctx):
        lspd = self.bot.get_guild(538426212863967242)
        async with self.config.guild(lspd).times() as time:
            async with self.config.guild(ctx.guild).times() as timess:
                for crime in time:
                    timess[crime] = time[crime]
        await ctx.send("Converted")

    @commands.command()
    async def addunit(self, ctx, unit: str, officers: commands.Greedy[discord.Member]):
        """Allow CO's to add division ranks."""
        teuc = 492941946554155028
        auc = 492942018058649602
        csuc = 492941760473989120
        isuc = 492942173407543308
        giuc = 454959597812318209
        rsuc = 432610381379141654
        tuc = 492942419944538112
        if unit.lower() == "teu":
            for role in ctx.author.roles:
                if role.id == teuc:
                    teu = 492941884394569739
                    teurole = discord.utils.get(ctx.guild.roles, id=teu)
                    for officer in officers:
                        try:
                            await officer.add_roles(teurole,
                                                    reason=f"{unit.upper()} role given to {officer.display_name} by {ctx.author.display_name}.")
                            await ctx.send(f"TEU role given to {officer.display_name} successfully.")
                        except:
                            await ctx.send("Request failed.")
        elif unit.lower() == "au":
            for role in ctx.author.roles:
                if role.id == auc:
                    au = 492942073700417547
                    teurole = discord.utils.get(ctx.guild.roles, id=au)
                    for officer in officers:
                        try:
                            await officer.add_roles(teurole,
                                                    reason=f"{unit.upper()} role given to {officer.display_name} by {ctx.author.display_name}.")
                            await ctx.send(f"AU role given to {officer.display_name} successfully.")
                        except:
                            await ctx.send("Request failed.")
        elif unit.lower() == "csu":
            for role in ctx.author.roles:
                if role.id == csuc:
                    csu = 492941595620933633
                    teurole = discord.utils.get(ctx.guild.roles, id=csu)
                    for officer in officers:
                        try:
                            await officer.add_roles(teurole,
                                                    reason=f"{unit.upper()} role given to {officer.display_name} by {ctx.author.display_name}.")
                            await ctx.send(f"CSU role given to {officer.display_name} successfully.")
                        except:
                            await ctx.send("Request failed.")
        elif unit.lower() == "isu":
            for role in ctx.author.roles:
                if role.id == isuc:
                    isu = 492942139475361803
                    teurole = discord.utils.get(ctx.guild.roles, id=isu)
                    for officer in officers:
                        try:
                            await officer.add_roles(teurole,
                                                    reason=f"{unit.upper()} role given to {officer.display_name} by {ctx.author.display_name}.")
                            await ctx.send(f"ISU role given to {officer.display_name} successfully.")
                        except:
                            await ctx.send("Request failed.")
        elif unit.lower() == "giu":
            for role in ctx.author.roles:
                if role.id == giuc:
                    giu = 454959515495038997
                    teurole = discord.utils.get(ctx.guild.roles, id=giu)
                    for officer in officers:
                        try:
                            await officer.add_roles(teurole,
                                                    reason=f"{unit.upper()} role given to {officer.display_name} by {ctx.author.display_name}.")
                            await ctx.send(f"GIU role given to {officer.display_name} successfully.")
                        except:
                            await ctx.send("Request failed.")
        elif unit.lower() == "rsu":
            for role in ctx.author.roles:
                if role.id == rsuc:
                    rsu = 432609459852935168
                    teurole = discord.utils.get(ctx.guild.roles, id=rsu)
                    for officer in officers:
                        try:
                            await officer.add_roles(teurole,
                                                    reason=f"{unit.upper()} role given to {officer.display_name} by {ctx.author.display_name}.")
                            await ctx.send(f"RSU role given to {officer.display_name} successfully.")
                        except:
                            await ctx.send("Request failed.")
        elif unit.lower() == "tu":
            for role in ctx.author.roles:
                if role.id == tuc:
                    tu = 492942456359223316
                    teurole = discord.utils.get(ctx.guild.roles, id=tu)
                    for officer in officers:
                        try:
                            await officer.add_roles(teurole,
                                                    reason=f"{unit.upper()} role given to {officer.display_name} by {ctx.author.display_name}.")
                            await ctx.send(f"TU role given to {officer.display_name} successfully.")
                        except:
                            await ctx.send("Request failed.")

    @commands.command()
    async def removeunit(self, ctx, unit: str, officers: commands.Greedy[discord.Member]):
        """Allow CO's to remove division ranks."""
        teuc = 492941946554155028
        auc = 492942018058649602
        csuc = 492941760473989120
        isuc = 492942173407543308
        giuc = 454959597812318209
        rsuc = 432610381379141654
        tuc = 492942419944538112
        if unit.lower() == "teu":
            for role in ctx.author.roles:
                if role.id == teuc:
                    teu = 492941884394569739
                    teurole = discord.utils.get(ctx.guild.roles, id=teu)
                    for officer in officers:
                        try:
                            await officer.remove_roles(teurole,
                                                       reason=f"{unit.upper()} role removed from {officer.display_name} by {ctx.author.display_name}.")
                            await ctx.send(f"TEU role removed from {officer.display_name} successfully.")
                        except:
                            await ctx.send("Request failed.")
        elif unit.lower() == "au":
            for role in ctx.author.roles:
                if role.id == auc:
                    au = 492942073700417547
                    teurole = discord.utils.get(ctx.guild.roles, id=au)
                    for officer in officers:
                        try:
                            await officer.remove_roles(teurole,
                                                       reason=f"AU role removed from {officer.display_name} by {ctx.author.display_name}.")
                            await ctx.send(f"AU role removed from {officer.display_name} successfully.")
                        except:
                            await ctx.send("Request failed.")
        elif unit.lower() == "csu":
            for role in ctx.author.roles:
                if role.id == csuc:
                    csu = 492941595620933633
                    teurole = discord.utils.get(ctx.guild.roles, id=csu)
                    for officer in officers:
                        try:
                            await officer.remove_roles(teurole,
                                                       reason=f"CSU role removed from {officer.display_name} by {ctx.author.display_name}.")
                            await ctx.send(f"CSU role removed from {officer.display_name} successfully.")
                        except:
                            await ctx.send("Request failed.")
        elif unit.lower() == "isu":
            for role in ctx.author.roles:
                if role.id == isuc:
                    isu = 492942139475361803
                    teurole = discord.utils.get(ctx.guild.roles, id=isu)
                    for officer in officers:
                        try:
                            await officer.remove_roles(teurole,
                                                       reason=f"ISU role removed from {officer.display_name} by {ctx.author.display_name}.")
                            await ctx.send(f"ISU role removed from {officer.display_name} successfully.")
                        except:
                            await ctx.send("Request failed.")
        elif unit.lower() == "giu":
            for role in ctx.author.roles:
                if role.id == giuc:
                    giu = 454959515495038997
                    teurole = discord.utils.get(ctx.guild.roles, id=giu)
                    for officer in officers:
                        try:
                            await officer.remove_roles(teurole,
                                                       reason=f"GIU role removed from {officer.display_name} by {ctx.author.display_name}.")
                            await ctx.send(f"GIU role removed from to {officer.display_name} successfully.")
                        except:
                            await ctx.send("Request failed.")
        elif unit.lower() == "rsu":
            for role in ctx.author.roles:
                if role.id == rsuc:
                    rsu = 432609459852935168
                    teurole = discord.utils.get(ctx.guild.roles, id=rsu)
                    for officer in officers:
                        try:
                            await officer.remove_roles(teurole,
                                                       reason=f"RSU role removed from {officer.display_name} by {ctx.author.display_name}.")
                            await ctx.send(f"RSU role removed from {officer.display_name} successfully.")
                        except:
                            await ctx.send("Request failed.")
        elif unit.lower() == "tu":
            for role in ctx.author.roles:
                if role.id == tuc:
                    tu = 492942456359223316
                    teurole = discord.utils.get(ctx.guild.roles, id=tu)
                    for officer in officers:
                        try:
                            await officer.remove_roles(teurole,
                                                       reason=f"TU role removed from {officer.display_name} by {ctx.author.display_name}.")
                            await ctx.send(f"TU role removed from {officer.display_name} successfully.")
                        except:
                            await ctx.send("Request failed.")
