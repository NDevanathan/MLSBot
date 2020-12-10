#MLSBot.py

import os

import discord
import emoji
from dotenv import load_dotenv

MLS_TO_EMOJI = {"test_mls_tx":emoji.emojize(':cowboy_hat_face:')}
EMOJI_TO_REGION = {emoji.emojize(':cowboy_hat_face:'):'testing_region'}
REGIONS_TO_SERVERS = {"testing_region":"https://discord.gg/U6DUeVVZpu"}
HELP_TEXT ="""Hi, I'm MLSBot, and I'm here to help!
Use `!mls` commands to talk to me.
`!mls help` will bring up this text.
Use `!mls emoji [an MLS name]` and I'll give you the two corresponding emojis.
Use `!mls regions` and I'll list out the regions for which we have servers.
Use `!mls server [valid region]` and I'll link you to the appropriate regional server.
Use `!mls search [two emojis or an MLS name]` and I'll link you to the appropriate server.
By default, I'll directly message you any info you request, but if you want it dropped in the text channel, add `gc` to the end of your command.
Remember, I'm sensitive to spacing, so I won't respond to a command that doesn't *start with* `!mls` and have 1 space between the appropriate command terms."""
REGIONS = """The valid regions are:
testing_region
"""
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

def getEmoji(content):
    i = 0
    
def getServer(content):
    i = 0

def getSearch(content):
    i = 0

@client.event
async def on_ready():
    for guild in client.guilds:
        if (guild.name in GUILD):
            print(f'{client.user} has connected to {guild.name}!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if ('!mls' == message.content[:4]):
        if ('help' == message.content[5:9]):
            if ('gc' == message.content[-2:]):
                await message.channel.send(HELP_TEXT)
            else:
                await message.author.create_dm()
                await message.author.dm_channel.send(HELP_TEXT)
        elif ('emoji' == message.content[5:10]):
            if ('gc' == message.content[-2:]):
                mls = message.content[10:-2].replace(' ','')
                if mls in MLS_TO_EMOJI:
                    await message.channel.send(MLS_TO_EMOJI[mls])
                else:
                    await message.channel.send("Unknown MLS abbreviation")
            else:
                mls = message.content[10:].replace(' ','')
                if mls in MLS_TO_EMOJI:
                    await message.author.create_dm()
                    await message.author.dm_channel.send(MLS_TO_EMOJI[mls])
                else:
                    await message.author.create_dm()
                    await message.author.dm_channel.send("Unknown MLS abbreviation")
        elif ('regions' == message.content[5:12]):
            if ('gc' == message.content[-2:]):
                await message.channel.send(REGIONS)
            else:
                await message.author.create_dm()
                await message.author.dm_channel.send(REGIONS)
        elif ('server' == message.content[5:11]):
            if ('gc' == message.content[-2:]):
                region = message.content[11:-2].replace(' ','')
                if region in REGIONS_TO_SERVERS:
                    await message.channel.send(REGIONS_TO_SERVERS[region])
                else:
                    await message.channel.send("Unknown region")
            else:
                region = message.content[11:].replace(' ','')
                if region in REGIONS_TO_SERVERS:
                    await message.author.create_dm()
                    await message.author.dm_channel.send(REGIONS_TO_SERVERS[region])
                else:
                    await message.author.create_dm()
                    await message.author.dm_channel.send("Unknown region")
        elif ('search' == message.content[5:11]):
            if ('gc' == message.content[-2:]):
                emote = message.content[11:-2].replace(' ','')
                if emote in EMOJI_TO_REGION:
                    region = EMOJI_TO_REGION[emote]
                    if region in REGIONS_TO_SERVERS:
                        await message.channel.send(emote + ', ' + region)
                        await message.channel.send(REGIONS_TO_SERVERS[region])
                    else:
                        await message.channel.send("Unknown emoji")
                else: 
                    await message.channel.send("Unknown emoji")
            else:
                emote = message.content[11:].replace(' ','')
                if emote in EMOJI_TO_REGION:
                    region = EMOJI_TO_REGION[emote]
                    if region in REGIONS_TO_SERVERS:
                        await message.author.create_dm()
                        await message.author.dm_channel.send(emote + ', ' + region)
                        await message.author.dm_channel.send(REGIONS_TO_SERVERS[region])
                    else:
                        await message.author.create_dm()
                        await message.author.dm_channel.send("Unknown emoji")
                else:
                    await message.author.create_dm()
                    await message.author.dm_channel.send("Unknown emoji")
        else:
            print(f'Recieved {message.system_content}')
            await message.channel.send("Unknown command")

client.run(TOKEN)