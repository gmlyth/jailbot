import os
import boto3

import discord

#Note: set the token. Duh.
DISCORD_TOKEN = os.environ['JAILBOT_TOKEN']

client = discord.Client()

@client.event
async def on_message(message):
    if message.content.startswith('https://www.nytimes.com'):
            skynet = discord.utils.get(client.emojis, name="skynet")
            await message.add_reaction(skynet)
            await message.channel.send('https://i.pinimg.com/originals/e6/df/a5/e6dfa50084fff4441d3b38f29303e930.jpg')
    return

client.run(DISCORD_TOKEN)