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

async def handle_get_emoji(message):
    mls = message.content[10:].replace(' gc','').replace(' ','')
    if mls in MLS_TO_EMOJI:
        await sendMsg(message, MLS_TO_EMOJI[mls])
    else:
        await sendMsg(message, "Unknown MLS abbreviation")

async def handle_get_server(message):
    region = message.content[11:].replace(' gc','').replace(' ','')
    if region in REGIONS_TO_SERVERS:
        await sendMsg(message, REGIONS_TO_SERVERS[region])
    else:
        await sendMsg(message, "Unknown region")

async def handle_get_search(message):
    emote = message.content[11:].replace(' gc','').replace(' ','')
    if emote in EMOJI_TO_REGION:
        region = EMOJI_TO_REGION[emote]
        if region in REGIONS_TO_SERVERS:
            await sendMsg(message, emote + ', ' + region)
            await sendMsg(message, REGIONS_TO_SERVERS[region])
        else:
            await sendMsg(message, "Unknown emoji")
    else: 
        await sendMsg(message, "Unknown emoji")

async def sendMsg(msg_in, msg_out):
    if ('gc' == msg_in.content[-2:]):
        await msg_in.channel.send(msg_out)
    else:
        await msg_in.author.create_dm()
        await msg_in.author.dm_channel.send(msg_out)

@client.event
async def on_ready():
    for guild in client.guilds:
        if (guild.name in GUILD):
            print(f'{client.user} has connected to {guild.name}!')

@client.event
async def on_message(message):
    if ('!mls' == message.content[:4]):
        if ('help' == message.content[5:9]):
            await sendMsg(message, HELP_TEXT)
        elif ('emoji' == message.content[5:10]):
            await handle_get_emoji(message)
        elif ('regions' == message.content[5:12]):
            await sendMsg(message, REGIONS)
        elif ('server' == message.content[5:11]):
            await handle_get_server(message)
        elif ('search' == message.content[5:11]):
            await handle_get_search(message)
        else:
            print(f'Recieved {message.system_content}')
            await message.channel.send("Unknown command")

client.run(TOKEN)