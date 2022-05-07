import os
import boto3

import discord
from discord.ext import commands 

ssm_client = boto3.client("ssm")

#Note: set the token. Duh.
#DISCORD_TOKEN = os.environ['JAILBOT_TOKEN']
DISCORD_TOKEN = ssm_client.get_parameter(Name='paywallbot-token')["Parameter"]["Value"]

bot = commands.Bot(command_prefix=".")

#Initialize collections.

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # if message.content.startswith('https://www.nytimes.com'):
    #         skynet = discord.utils.get(bot.emojis, name="skynet")
    #         await message.add_reaction(skynet)
    #         await message.channel.send('https://i.pinimg.com/originals/e6/df/a5/e6dfa50084fff4441d3b38f29303e930.jpg')
    # process message against known paywalls. If a match, add a reaction (if any exist for server) and send a reply.
    await bot.process_commands(message)
    return

@bot.command(help="This will register the domain of the url that's passed in as a paywall, and ignores it if it's not in the expected format.",
	brief="Registers a paywall.")
async def paywall(ctx, arg):
    response = await register_paywall(ctx, arg)
    await ctx.channel.send(response)
    return

@bot.command(help="This will register a custom emoji from the server in question as a response to a paywall - just on that server.",
	brief="Registers an emoji response.")
async def emoji(ctx, arg):
    parts = arg.split(':')
    response = await register_emoji(ctx, parts[1], parts[2].replace('>',''))
    await ctx.channel.send(response)   
    return

@bot.command(help="This will register a text value as a response to a paywall - just on that server.",
	brief="Registers a text response.")
async def reply(ctx, *args):
    msg = ""
    for arg in args:
        msg = msg + " " + arg
    response = await register_reply(ctx, msg)
    await ctx.channel.send(response)   
    return     

async def register_paywall(ctx, paywall_url):
    result = f"Now we'd add {paywall_url} as a registered paywall."
    return result

async def register_emoji(ctx, emoji_name, emoji_id):
    result = f"Now we'd add {emoji_name} (id:{emoji_id}) as a registered emjoi response for server {ctx.guild.name}."
    return result

async def register_reply(ctx, reply):
    result = f"Now we'd add {reply} as a registered text (or image) response for server {ctx.guild.name}."
    return result

bot.run(DISCORD_TOKEN)