import discord
from discord.ext import commands
import dataset
import json
import utils
from safeembeds import patch_discord
import typing

patch_discord()

with open("config.json", "r") as f:
    config = json.load(f)

db = dataset.connect("sqlite:///DB.db")
Punishments = db["Punishments"]
Guilds = db["Guilds"]

bot = commands.Bot(command_prefix=config["prefix"])

@bot.event
async def on_ready():
    print(f"""
Bot online and ready as {bot.user.name} ({bot.user.id})
Bot developed by Lewis L. Foster 2020""")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

@bot.command(name="owo", hidden=True)
async def owo(ctx):
    await ctx.send("OwO")

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
@commands.bot_has_permissions(kick_members=True)
async def kick_command(ctx, members: commands.Greedy[typing.Union[discord.Member, discord.User]], *, reason: str = "No reason given"):
    """
    Kick one or more member(s) from the server
    """
    successfull = []
    failed = []
    for member in members:
        try:
            pid = utils.idutils.generate_id()
            print(pid)
            try:
                await member.send(embed=discord.Embed(title=f"Kicked from {ctx.guild.name}", description="You were kicked from `{ctx.guild.name}` for the reason `{reason}`").set_footer(text=f"Punishment ID: {pid}"))
            except:
                pass
            await member.kick(reason=f"{reason} - Responsible User: @{ctx.author.name}#{ctx.author.discriminator} Bot Punishment ID: {pid}")
            Punishments.insert(dict(id=pid, user=member.id, moderator=ctx.author.id, reason=reason, removed=0, type="kick", guild=ctx.guild.id))
            successfull.append(member)
        except Exception as e:
            failed.append(member)
            print(e)
    if len(successfull) == 0 and len(failed) >= 1 and len(members) > 1:
        return await ctx.send(embed=discord.Embed(title="Failed to kick all members", description="Check that the member(s) given are in the server and try the command again"))
    kicked = ""
    sfailed = ""
    for x in successfull:
        kicked = kicked + "{} - {}\n".format(x[0].name, x[1])
    for x in failed:
        sfailed = sfailed + "{} - {}\n".format(x[0].name, x[1])
    if len(successfull) > 0:
        await ctx.send(embed=discord.Embed(title=f"Kicked {len(successfull)} members", description=kicked))
    if len(failed) > 0:
        await ctx.send(embed=discord.Embed(title="Failed to kick the following users", description=failed))

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
@commands.bot_has_permissions(ban_members=True)
async def ban_command(ctx, members: commands.Greedy[typing.Union[discord.Member, discord.User]], *, reason: str = "No reason given"):
    """
    Ban one or more member(s) from the server
    """
    successfull = []
    failed = []
    for member in members:
        try:
            pid = utils.idutils.generate_id()
            try:
                embed = discord.Embed(title=f"Banned from {ctx.guild.name}", description=f"You were banned from `{ctx.guild.name}` for the reason `{reason}`")
                embed.set_footer(text=f"Punishment ID: {pid}")
                await member.send(embed=embed)
            except:
                pass
            await member.ban(reason=f"{reason} - Responsible User: @{ctx.author.name}#{ctx.author.discriminator} Bot Punishment ID: {pid}")
            Punishments.insert(dict(id=pid, user=member.id, moderator=ctx.author.id, reason=reason, removed=0, type="ban", guild=ctx.guild.id))
            successfull.append([member, pid])
        except Exception as e:
            failed.append([member, pid])
            print(e)
    if len(successfull) == 0 and len(failed) >= 1 and len(members) > 1:
        return await ctx.send(embed=discord.Embed(title="Failed to ban all members", description="Check that the member(s) given exist and try the command again"))
    banned = ""
    sfailed = ""
    for x in successfull:
        banned = banned + "{} - {}\n".format(x[0].name, x[1])
    for x in failed:
        sfailed = sfailed = "{} - {}\n".format(x[0].name, x[1])
    if len(successfull) > 0:
        await ctx.send(embed=discord.Embed(title=f"Banned {len(successfull)} members", description=banned))
    if len(failed) > 0:
        await ctx.send(embed=discord.Embed(title="Failed to banned the following users", description=sfailed))

@bot.command(name="strike")
@commands.has_permissions(manage_messages=True)
async def strike_command(ctx, members: commands.Greedy[typing.Union[discord.Member, discord.User]], *, reason: str = "No reason given"):
    """
    Issue a strike/warning to one or more member(s) from the server
    """
    striken = []
    for member in members:
        try:
            pid = utils.idutils.generate_id()
            try:
                embed = discord.Embed(title=f"Striken in {ctx.guild.name}", description=f"You were striken in `{ctx.guild.name}` for the reason `{reason}`")
                embed.set_footer(text=f"Punishment ID: {pid}")
                await member.send(embed=embed)
            except Exception as e:
                print(e)
                pass
            Punishments.insert(dict(id=pid, user=member.id, moderator=ctx.author.id, reason=reason, removed=0, type="strike", guild=ctx.guild.id))
            striken.append([member, pid])
        except Exception as e:
            print(e)
    str_striken = ""
    for x in striken:
        str_striken = str_striken + "{} - {}\n".format(x[0].name, x[1])
    await ctx.send(embed=discord.Embed(title="Issued a strike to the following users", description=str_striken))

@bot.command(name="setmuterole")
@commands.has_permissions(manage_guild=True)
async def set_muted_role(ctx, role: discord.Role):
    """
    Sets the server's muted role
    """
    try:
        Guilds.update(dict(id=ctx.guild.id, muterole=role.id), ["id"])
        await ctx.send(embed=discord.Embed(title="Updated Guild Muted Role", description=f"Updated the guild's muted role to {role.mention}"))
    except Exception as e:
        print(e)
        await ctx.send(embed=discord.Embed(title="An Error Occurred", discription="An errpr occurred when trying to update the guild role, please contact my developer"))

@bot.command(name="mute")
@commands.has_permissions(kick_members=True)
@commands.bot_has_permissions(manage_roles=True)
async def mute_command(ctx, member: discord.Member, *, reason="No reason given"):
    """
    Mute a member of the server
    """
    try:
        roles = member.roles
        oldroles = ",".join(str(x.id) for x in roles)
        pid = utils.idutils.generate_id()
        try:
            embed = discord.Embed(title=f"Muted in {ctx.guild.name}", description=f"You were muted in `{ctx.guild.name}` for the reason `{reason}`")
            embed.set_footer(text=f"Punishment ID: {pid}")
            await member.send(embed=embed)
        except Exception as e:
            print(e)
            pass
        mutedrole = ctx.guild.get_role(Guilds.find_one(id=ctx.guild.id)["muterole"])
        await member.edit(roles=[mutedrole], reason=f"{reason} - Responsible User: @{ctx.author.name}#{ctx.author.discriminator} Bot Punishment ID: {pid}")
        Punishments.insert(dict(id=pid, user=member.id, moderator=ctx.author.id, reason=reason, removed=0, type="mute", guild=ctx.guild.id, oldroles=oldroles))
        await ctx.send(embed=discord.Embed(title=f"Muted {member.name}", description=f"Successfully muted {member.mention} \nPunishment ID: {pid}"))
    except Exception as e:
        print(e)
        await ctx.send(embed=discord.Embed(title="An Error Occurred", description="Check that I have the `Manage Roles` permission and try again. If this error persists, please contact my developer"))

@bot.command(name="unmute")
@commands.has_permissions(kick_members=True)
@commands.bot_has_permissions(manage_roles=True)
async def unmute_command(ctx, member: discord.Member):
    """
    Unmutes a already muted member
    """
    try:
        currentmute = Punishments.find_one(user=member.id, type="mute", guild=ctx.guild.id, removed=0)
        pid = currentmute["id"]
        oldroles = []
        for role in currentmute["oldroles"].split(","):
            try:
                oldroles.append(ctx.guild.get_role(int(role)))
            except:
                pass
        await member.edit(roles=oldroles, reason=f"Unmuted by {ctx.author.name}")
        Punishments.update(dict(id=pid, removed=1), ["id"])
        try:
            embed = discord.Embed(title=f"Unmuted in {ctx.guild.name}", description=f"You were unmuted in `{ctx.guild.name}`")
            embed.set_footer(text=f"Punishment ID: {pid}")
            await member.send(embed=embed)
        except Exception as e:
            print(e)
            pass
        await ctx.send(embed=discord.Embed(title=f"Unmuted {member.name}", description=f"Successfully unmuted {member.mention} \nPunishment ID: {pid}"))
    except Exception as e:
        print(e)
        await ctx.send(embed=discord.Embed(title="An Error Occurred", description="Check that I have the `Manage Roles` permission and try again. If this error persists, please contact my developer"))

@bot.command(name="purgeall")
@commands.has_permissions(manage_messages=True)
@commands.bot_has_permissions(manage_messages=True)
async def purgeall_command(ctx, number: int):
    try:
        if number > 100:
            return await ctx.send(embed=discord.Embed(title="Failed to Purge", description="I can not purge more than 100 messages at a time due to discord's restrictions"))

        deleted = await ctx.channel.purge(limit=number+1 if number < 100 else number)
        await ctx.channel.send(embed=discord.Embed(title="Purge", description=f"Purged {len(deleted)} in {ctx.channel.mention}"), delete_after=10)
    except Exception as e:
        print(e)
        await ctx.send(embed=discord.Embed(title="An Error Occurred", description="Check that I have the `Manage Messages` permission and try again. If this error persists, please contact my developer"))

@bot.command(name="purge")
@commands.has_permissions(manage_messages=True)
@commands.bot_has_permissions(manage_messages=True)
async def purgeall_command(ctx, member: discord.Member, number: int):
    try:
        if number > 100:
            return await ctx.send(embed=discord.Embed(title="Failed to Purge", description="I can not purge more than 100 messages at a time due to discord's restrictions"))

        def check(m):
            return m.author == member

        deleted = await ctx.channel.purge(limit=number+1 if number < 100 else number, check=check)
        await ctx.channel.send(embed=discord.Embed(title="Purge", description=f"Purged {len(deleted)} in {ctx.channel.mention} from {member.mention}"), delete_after=10)
    except Exception as e:
        print(e)
        await ctx.send(embed=discord.Embed(title="An Error Occurred", description="Check that I have the `Manage Messages` permission and try again. If this error persists, please contact my developer"))


bot.run(config["token"])
