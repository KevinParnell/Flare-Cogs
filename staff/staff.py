import discord
from redbot.core import commands, checks, Config
import random
from collections import namedtuple

BaseCog = getattr(commands, "Cog", object)


class Staff(BaseCog):
    """WC-RP's Commands"""

    @commands.command(aliases=["ateam", "adminteam", "admins"])
    async def staff(self, ctx):
        """WC-RP Staff Team"""
        colour = discord.Color.from_hsv(random.random(), 1, 1)
        embed = discord.Embed(
            title="WC-RP Staff Team", colour=colour)
        embed.add_field(name="\N{ZERO WIDTH SPACE}", value="\N{ZERO WIDTH SPACE}", inline=True)
        embed.add_field(name="Administration Team", value="\N{ZERO WIDTH SPACE}", inline=True)
        embed.add_field(name="\N{ZERO WIDTH SPACE}", value="\N{ZERO WIDTH SPACE}", inline=True)
        for member in ctx.guild.members:
            if member.top_role.name == "Lead Administrator":
                embed.add_field(name="Lead Admin", value=member.display_name, inline=True)
        for member in ctx.guild.members:
            if member.top_role.name == "Senior Administrator":
                embed.add_field(name="Senior Administrator", value=member.display_name, inline=True)
        for member in ctx.guild.members:
            if member.top_role.name == "Administrator":
                embed.add_field(name="Administrator", value=member.display_name, inline=True)
        for member in ctx.guild.members:
            if member.top_role.name == "IG Moderator":
                embed.add_field(name="Moderator", value=member.display_name, inline=True)

        embed.add_field(name="\N{ZERO WIDTH SPACE}", value="\N{ZERO WIDTH SPACE}", inline=True)

        embed.add_field(name="\N{ZERO WIDTH SPACE}", value="\N{ZERO WIDTH SPACE}", inline=True)

        embed.add_field(name="\N{ZERO WIDTH SPACE}", value="\N{ZERO WIDTH SPACE}", inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def management(self, ctx):
        """WC-RP Management"""
        colour = discord.Color.from_hsv(random.random(), 1, 1)
        embed = discord.Embed(
            title="WC-RP Management Team", colour=colour)
        embed.add_field(name="\N{ZERO WIDTH SPACE}", value="\N{ZERO WIDTH SPACE}", inline=True)
        embed.add_field(name="Management", value="\N{ZERO WIDTH SPACE}", inline=True)
        embed.add_field(name="\N{ZERO WIDTH SPACE}", value="\N{ZERO WIDTH SPACE}", inline=True)
        for member in ctx.guild.members:
            if member.top_role.name == "Server Owner":
                embed.add_field(name="Server Owner", value=member.display_name, inline=True)
        for member in ctx.guild.members:
            if member.top_role.name == "Server Management":
                embed.add_field(name="Server Manager", value=member.display_name, inline=True)
        for member in ctx.guild.members:
            if member.top_role.name == "Scripter":
                embed.add_field(name="Scripter", value=member.display_name, inline=True)
        for member in ctx.guild.members:
            if member.top_role.name == "Lead Administrator":
                embed.add_field(name="Lead Admin", value=member.display_name, inline=True)
        embed.add_field(name="\N{ZERO WIDTH SPACE}", value="\N{ZERO WIDTH SPACE}", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_any_role("Moderator", "Scipter",  "IG Moderator", "Server Management", "Server Owner", "Senior Administrator", "Administrator", "Staff")
    async def pm(self, ctx: commands.Context, user_id: int, *, message: str):
        """Sends a DM to a user

        This command needs a user id to work.
        To get a user id enable 'developer mode' in Discord's
        settings, 'appearance' tab. Then right click a user
        and copy their id"""
        destination = discord.utils.get(ctx.bot.get_all_members(), id=user_id)
        description = "Reply from WC-RP Staff Member {}".format(ctx.author.display_name)
        content = "You can reply to this message just by replying here."
        if await ctx.embed_requested():
            e = discord.Embed(colour=discord.Colour.red(), description=message)

            e.set_footer(text=content)
            if ctx.bot.user.avatar_url:
                e.set_author(name=description, icon_url=ctx.bot.user.avatar_url)
            else:
                e.set_author(name=description)

            try:
                await destination.send(embed=e)
            except discord.HTTPException:
                await ctx.send(
                    "Sorry, I couldn't deliver your message to {}").format(destination)
            else:
                await ctx.send("Message delivered to {}".format(destination))
        else:
            response = "{}\nMessage:\n\n{}".format(description, message)
            try:
                await destination.send("{}\n{}".format(box(response), content))
            except discord.HTTPException:
                await ctx.send(
                    "Sorry, I couldn't deliver your message to {}").format(destination)
            else:
                await ctx.send"Message delivered to {}".format(destination))
