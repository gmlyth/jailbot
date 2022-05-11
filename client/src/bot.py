import os
import boto3
import cache
import random
import utils
from urllib.parse import urlparse

import discord
from discord.ext import commands 

ssm_client = boto3.client('ssm', region_name='us-east-2')

#Note: set the token. Duh.
#DISCORD_TOKEN = os.environ['JAILBOT_TOKEN']
DISCORD_TOKEN = ssm_client.get_parameter(Name='paywallbot-token')["Parameter"]["Value"]

bot = commands.Bot(command_prefix=".")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
  
    if message.content.startswith('.') == False:
        if await is_paywall(message.content):
            emoji = await get_emoji(message.guild.id)
            reply = await get_reply(message.guild.id)
            if emoji != None:
                await message.add_reaction(emoji)
            if reply != None:
                await message.channel.send(reply)
    
    await bot.process_commands(message)
    return

@bot.command(help="This will register the domain of the url that's passed in as a paywall, and ignores it if it's not in the expected format.",
	brief="Registers a paywall.")
async def paywall(ctx, arg):
    if await is_blocked_user(ctx.message.author.id):
        response = f'<@{ctx.message.author.id}> I won\'t even dignify that with a response.'
    else:
        response = await register_paywall(ctx.guild.name, ctx.guild.id, arg)
    await ctx.channel.send(response)
    return

@bot.command(help="This will register a custom emoji from the server in question as a response to a paywall - just on that server.",
	brief="Registers an emoji response.")
async def emoji(ctx, arg):
    if await is_blocked_user(ctx.message.author.id):
        response = f'<@{ctx.message.author.id}> I won\'t even dignify that with a response.'
    else:
        parts = arg.split(':')
        response = await register_emoji(ctx.guild.name, ctx.guild.id, parts[1], int(parts[2].replace('>','')))
    await ctx.channel.send(response)   
    return

@bot.command(help="This will register a text value as a response to a paywall - just on that server.",
	brief="Registers a text response.")
async def reply(ctx, *args):
    if await is_blocked_user(ctx.message.author.id):
        response = f'<@{ctx.message.author.id}> I won\'t even dignify that with a response.'
    else:
        msg = ""
        for arg in args:
            msg = msg + " " + arg
        response = await register_reply(ctx.guild.name, ctx.guild.id, msg)
    await ctx.channel.send(response)   
    return  

@bot.command(help="This blocks a user from registering paywalls, emojis, or replies (or blocking another user).")
async def block(ctx, *args):
    if await is_blocked_user(ctx.message.author.id):
        response = f'<@{ctx.message.author.id}> I won\'t even dignify that with a response.'
    else:
        id = ctx.message.mentions[0].id
        name = ctx.message.mentions[0].display_name
        response = await register_blocked_user(ctx.guild.name, ctx.guild.id, name, id)
    await ctx.channel.send(response)
    return 

@bot.command(help="This will list paywalls, emojis, and replies for the current server.")
async def paywalls(ctx):
    embed=discord.Embed(title="Paywalls", url="https://github.com/gmlyth/paywallbot"
        , description=f'This is a list of the registered paywall info for {ctx.guild.name}', color=0xFF5733)
    embed.set_author(name=bot.user.display_name, url="https://github.com/gmlyth/paywallbot", icon_url=bot.user.avatar_url)
    paywalls_value = 'There are no paywalls on this server. Type ".paywall (some url) to add one!"'
    emojis_value = 'There are no emoji responses on this server. Type ".emoji to add one!"'
    replies_value = 'There are no text responses on this server. Type ".reply to add one!"'
    blocked_users_value = 'There are no blocked users on this server. Type ".block to block someone!"'
    if len(cache.PAYWALLS) > 0:
        paywalls_value = ''
        for dict in cache.PAYWALLS:
            paywalls_value = paywalls_value + dict['paywall_url'] + '\n'
    if len(cache.EMOJIS) > 0:
        emojis_value = ''
        for dict in cache.EMOJIS:
            emojis_value = emojis_value + f':{dict["emoji_name"]}:' + '\n'
    if len(cache.REPLIES) > 0:
        replies_value = ''
        for dict in cache.REPLIES:
            replies_value = replies_value + dict['reply'] + '\n'     
    if len(cache.BLOCKED_USERS) > 0:
        blocked_users_value = ''
        for dict in cache.BLOCKED_USERS:
            blocked_users_value = blocked_users_value + f'<@{dict["user_id"]}>' + '\n'               
    embed.add_field(name="Paywalls", value=paywalls_value, inline=False)
    embed.add_field(name="Emojis", value=emojis_value, inline=False)
    embed.add_field(name="Replies", value=replies_value, inline=False)
    embed.add_field(name="Blocked Users", value=blocked_users_value, inline=False)
    await ctx.send(embed=embed)   
    return  

@bot.event
async def on_ready(): 
    #https://www.youtube.com/watch?v=SMTDQZzQMKk
    return 

async def register_paywall(guild_name, guild_id, paywall_url):
    hostname = await utils.get_hostname(paywall_url)
    if await is_paywall(hostname):
        result = f'{hostname} is already a paywall on this server.'
    else:
        obj = {'guild_name': guild_name, 'guild_id': guild_id, 'paywall_url': hostname}
        cache.PAYWALLS.append(obj)
        table = cache.dynamodb_client.Table('PaywallBotPaywall')
        table.put_item(Item=obj)
        result = f'Added {hostname} to paywalls.'
    return result

async def register_blocked_user(guild_name, guild_id, user_name, user_id):
    if await is_blocked_user(user_id):
        result = f':<@{user_id}> is already a blocked user on this server.'
    else:
        obj = {'guild_name': guild_name, 'guild_id': guild_id, 'user_name': user_name, 'user_id': user_id}
        cache.BLOCKED_USERS.append(obj)
        table = cache.dynamodb_client.Table('PaywallBotBlockedUser')
        table.put_item(Item=obj)   
        result = f'<@{user_id}> has been blocked from messing with this bot.'
    return result

async def register_emoji(guild_name, guild_id, emoji_name, emoji_id):
    if await is_emoji(emoji_name):
        result = f':{emoji_name}: is already an emoji response on this server.'
    else:
        obj = {'guild_name': guild_name, 'guild_id': guild_id, 'emoji_name': emoji_name, 'emoji_id': emoji_id}
        cache.EMOJIS.append(obj)
        table = cache.dynamodb_client.Table('PaywallBotEmoji')
        table.put_item(Item=obj)   
        result = f'Added :{emoji_name}: as a registered emoji response.'
    return result

async def register_reply(guild_name, guild_id, reply):
    if await is_reply(reply):
        result = f'{reply} is already a text response on this server.'
    else:
        obj = {'guild_name': guild_name, 'guild_id': guild_id, 'reply': reply}
        cache.REPLIES.append(obj)
        table = cache.dynamodb_client.Table('PaywallBotReply')
        table.put_item(Item=obj)    
        result = f'Added "{reply}" as a registered text response.'
    return result

#todo: check based on guild id.
async def is_paywall(message):
    result = False
    
    for dict in cache.PAYWALLS:
        if message.__contains__(dict["paywall_url"]):
            result = True
            break
    return result

#todo: check based on guild id.
async def is_emoji(emoji):
    result = False
    
    for dict in cache.EMOJIS:
        if emoji == dict["emoji_name"]:
            result = True
            break
    return result

#todo: check based on guild id.
async def is_blocked_user(user_id):
    result = False
    
    for dict in cache.BLOCKED_USERS:
        if user_id == dict["user_id"]:
            result = True
            break
    return result

#todo: check based on guild id.
async def is_reply(reply):
    reply = False
    
    for dict in cache.REPLIES:
        if reply == dict["reply"]:
            reply = True
            break
    return reply

async def get_emoji(guild_id):
    emoji = None

    if len(cache.EMOJIS) > 0:
        itm = random.choice(cache.EMOJIS)
        emoji = itm['emoji_name']

    result = discord.utils.get(bot.emojis, name=emoji)
    return result

async def get_reply(guild_id):
    result = None

    if len(cache.REPLIES) > 0:
        itm = random.choice(cache.REPLIES)
        result = itm['reply']

    return result    

@bot.command()
async def quit(ctx):
    await ctx.send("Shutting down the bot")
    return await bot.logout() # this just shuts down the bot.

bot.run(DISCORD_TOKEN)