from redbot.core import commands, Config, checks
from redbot.core.utils.chat_formatting import pagify
import discord


class Modmail(commands.Cog):
    """Forward messages to set channels."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1398467138476)
        default_global = {
            "modmail": {},
            "toggle": {"status": True, "dms": True, "respond": True, "reply": None},
            "ignore": [],
        }
        self.config.register_global(**default_global)

    async def channelsend(self, embed2):
        async with self.config.toggle() as toggle:
            if not toggle["status"]:
                return
        async with self.config.modmail() as modmail:
            for stats in modmail:
                channel = self.bot.get_channel(modmail[stats])
                await channel.send(embed=embed2)

    @commands.Cog.listener()
    async def on_message_without_command(self, message):
        if message.guild is not None:
            return
        if message.author == self.bot.user:
            return
        async with self.config.ignore() as ignore:
            if message.author.id in ignore:
                return
        async with self.config.toggle() as toggle:
            if not toggle["dms"]:
                return
        embeds = []
        attachments_urls = []
        embeds.append(discord.Embed(description=message.content))
        embeds[0].set_author(
            name=f"{message.author} | {message.author.id}", icon_url=message.author.avatar_url
        )
        for attachment in message.attachments:
            if any(attachment.filename.endswith(imageext) for imageext in ["jpg", "png", "gif"]):
                if embeds[0].image:
                    embed = discord.Embed()
                    embed.set_image(url=attachment.url)
                    embeds.append(embed)
                else:
                    embeds[0].set_image(url=attachment.url)
            else:
                attachments_urls.append(f"[{attachment.filename}]({attachment.url})")
        if attachments_urls:
            embeds[0].add_field(name="Attachments", value="\n".join(attachments_urls))
        embeds[-1].timestamp = message.created_at
        for embed in embeds:
            await self.channelsend(embed)
        async with self.config.toggle() as toggle:
            if "respond" not in toggle:
                return
            if not toggle["respond"]:
                return
            else:
                reply = "Your message has been delivered."
                if toggle["reply"] is not None:
                    reply = toggle["reply"]
                await message.author.send(f"{reply}")

    @checks.admin_or_permissions(manage_channels=True)
    @commands.group(autohelp=True)
    async def modmailset(self, ctx):
        """Modmail Commands"""
        pass

    @commands.command()
    async def modmail(self, ctx, *, content: str = None):
        """Manually send modmail."""
        async with self.config.ignore() as ignore:
            if ctx.author.id in ignore:
                return
        if ctx.message.attachments or content:
            embeds = []
            attachments_urls = []
            embeds.append(discord.Embed(description=content))
            embeds[0].set_author(
                name=f"{ctx.author} | {ctx.author.id}", icon_url=ctx.author.avatar_url
            )
            for attachment in ctx.message.attachments:
                if any(
                    attachment.filename.endswith(imageext) for imageext in ["jpg", "png", "gif"]
                ):
                    if embeds[0].image:
                        embed = discord.Embed()
                        embed.set_image(url=attachment.url)
                        embeds.append(embed)
                    else:
                        embeds[0].set_image(url=attachment.url)
                else:
                    attachments_urls.append(f"[{attachment.filename}]({attachment.url})")
            if attachments_urls:
                embeds[0].add_field(name="Attachments", value="\n".join(attachments_urls))
            embeds[-1].timestamp = ctx.message.created_at
            for embed in embeds:
                await self.channelsend(embed)
            async with self.config.toggle() as toggle:
                if "respond" not in toggle:
                    return
                if not toggle["respond"]:
                    return
                else:
                    reply = "Your message has been delivered."
                    if toggle["reply"] is not None:
                        reply = toggle["reply"]
                    await ctx.send(f"{reply}")

    @checks.is_owner()
    @modmailset.command()
    async def channel(self, ctx, channel: discord.TextChannel):
        """Set the channel that the bot will post to - Mention the channel."""
        async with self.config.modmail() as modmail:
            key = str(ctx.message.guild.id)
            modmail[key] = channel.id
        await ctx.send("Channel added successfully.")

    @checks.is_owner()
    @modmailset.command()
    async def remove(self, ctx, channel: discord.TextChannel):
        """Remove a current channel from the modmail listing."""
        async with self.config.modmail() as modmail:
            key = str(ctx.message.guild.id)
            if key in modmail:
                del modmail[key]
                await ctx.send("Channel removed successfully.")
            else:
                await ctx.send("This channel does not current have a modmail channel configured.")

    @checks.is_owner()
    @modmailset.command(name="list")
    async def _list(self, ctx):
        """List all current modmail channels."""
        async with self.config.modmail() as modmail:
            if not modmail:
                await ctx.send("No channels are currently set.")
            for stats in modmail:
                await ctx.send(modmail[stats])

    @checks.is_owner()
    @modmailset.command()
    async def toggle(self, ctx, mode: bool):
        """Toggle modmail on the current channel."""
        async with self.config.toggle() as toggle:
            if mode:
                toggle["status"] = True
                await ctx.send("Modmail is now enabled.")
            else:
                toggle["status"] = False
                await ctx.send("Modmail is now disabled.")

    @checks.is_owner()
    @modmailset.command()
    async def dms(self, ctx, mode: bool):
        """Toggle modmail forwarding from DMs.
           True - Allow DM Forwarding.
           False - Disallow DM Forwarding."""
        async with self.config.toggle() as toggle:
            if mode:
                toggle["dms"] = True
                await ctx.send("Modmail will now forward all DMs.")
            else:
                toggle["dms"] = False
                await ctx.send("Modmail will no longer forward every message sent via DM.")

    @checks.is_owner()
    @modmailset.command()
    async def respond(self, ctx, mode: bool):
        """Toggle responding to modmail."""
        async with self.config.toggle() as toggle:
            if mode:
                toggle["respond"] = True
                await ctx.send(
                    "A confirmation message will be sent when a modmail is delivered, you can configure a response using [p]modmailset respondmsg."
                )
            else:
                toggle["respond"] = False
                await ctx.send("A confirmation message will no longer be sent.")

    @checks.is_owner()
    @modmailset.command()
    async def respondmsg(self, ctx, *, reply: str = None):
        """Set your response message for modmails."""
        async with self.config.toggle() as toggle:
            if reply is None:
                toggle["reply"] = None
                await ctx.send("The confirmation message has been reset.")
            else:
                toggle["reply"] = reply
                await ctx.send(f"Your confirmation message has been configured to: `{reply}`")

    @checks.admin_or_permissions(manage_channels=True)
    @modmailset.command()
    async def ignore(self, ctx, user: discord.Member):
        """Ignore a user from using the modmail."""
        async with self.config.ignore() as ignore:
            ignore.append(user.id)
            await ctx.send("User has been added to the list.")

    @checks.admin_or_permissions(manage_channels=True)
    @modmailset.command()
    async def unignore(self, ctx, user: discord.Member):
        """Remove user from the ignored list."""
        async with self.config.ignore() as ignore:
            ignore.remove(user.id)
            await ctx.send("User has been removed from the list.")

    @checks.mod()
    @commands.command()
    async def reply(self, ctx, user: discord.Member, *, message: str):
        """Reply to a modmail."""
        e = discord.Embed(colour=discord.Colour.red(), description=message)
        if ctx.bot.user.avatar_url:
            e.set_author(
                name=f"Message from {ctx.author} | {ctx.author.id}",
                icon_url=ctx.bot.user.avatar_url,
            )
        else:
            e.set_author(name=f"Message from {ctx.author} | {ctx.author.id}")

        try:
            await user.send(embed=e)
        except discord.HTTPException:
            await ctx.send("Sorry, I couldn't deliver your message to {}".format(user))
        else:
            await ctx.send("Message delivered to {}".format(user))

    @checks.admin()
    @modmailset.command()
    async def ignoredlist(self, ctx):
        """List ignored users."""
        ignored = []
        async with self.config.ignore() as ignore:
            if not ignore:
                await ctx.send("The ignored list is currently empty.")
                return
            for user in ignore:
                uid = self.bot.get_user(int(user))
                ignored.append(f"{uid.name} - {user}")
        users = "\n".join(ignored)
        for page in pagify(users):
            await ctx.send(page)
