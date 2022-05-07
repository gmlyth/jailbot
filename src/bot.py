import os
import boto3
import cache
import random

import discord
from discord.ext import commands 

ssm_client = boto3.client("ssm")

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
    response = await register_paywall(ctx.guild.name, ctx.guild.id, arg)
    await ctx.channel.send(response)
    return

@bot.command(help="This will register a custom emoji from the server in question as a response to a paywall - just on that server.",
	brief="Registers an emoji response.")
async def emoji(ctx, arg):
    parts = arg.split(':')
    response = await register_emoji(ctx.guild.name, ctx.guild.id, parts[1], parts[2].replace('>',''))
    await ctx.channel.send(response)   
    return

@bot.command(help="This will register a text value as a response to a paywall - just on that server.",
	brief="Registers a text response.")
async def reply(ctx, *args):
    msg = ""
    for arg in args:
        msg = msg + " " + arg
    response = await register_reply(ctx.guild.name, ctx.guild.id, msg)
    await ctx.channel.send(response)   
    return  

@bot.event
async def on_ready(): 
    #https://www.youtube.com/watch?v=SMTDQZzQMKk
    return 

async def register_paywall(guild_name, guild_id, paywall_url):
    #result = f"Now we'd add {paywall_url} as a registered paywall."
    obj = {'paywall_url': paywall_url}
    cache.PAYWALLS.append(obj)
    result = f'Added {paywall_url} to paywalls.'
    return result

async def register_emoji(guild_name, guild_id, emoji_name, emoji_id):
    obj = {'guild_name': guild_name, 'guild_id': guild_id, 'emoji_name': emoji_name, 'emoji_id': emoji_id}
    cache.EMOJIS.append(obj)
    result = f'Added :{emoji_name}: as a registered emjoi response.'
    return result

async def register_reply(guild_name, guild_id, reply):
    obj = {'guild_name': guild_name, 'guild_id': guild_id, 'reply': reply}
    cache.REPLIES.append(obj)
    result = f'Added :{reply}: as a registered text response.'
    return result

async def is_paywall(message):
    result = False
    
    for dict in cache.PAYWALLS:
        if message.__contains__(dict["paywall_url"]):
            result = True
            break
    return result

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

bot.run(DISCORD_TOKEN)