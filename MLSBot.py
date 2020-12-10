#MLSBot.py
"""
@author: Nikhil Devanathan
This script handles the functionality of MLSBot, a discord bot that organizes and helps users of discord servers that host
Multiple Listing Service (MLS) real estate data. Some of the key functionalities of MLSBot are populating regional servers with
appropriate text channels corresponding to different MLSs and helping users navigate the servers and chennels to reach their
desired MLS.
"""
import os

import discord
import emoji
from dotenv import load_dotenv

"""Because MLS codes can get quite cumbersome, channels are named using a combination
of two emojis. The first is a state identifier, and the second distinguishes the MLS.
This bot uses to below dicts to provide a painless interface for users to derive  
emojis from known MLS codes and use emojis to find the correct server."""
MLS_TO_EMOJI = {"test_mls_tx":emoji.emojize(':cowboy_hat_face:')}
EMOJI_TO_REGION = {emoji.emojize(':cowboy_hat_face:'):'testing_region'}
REGIONS_TO_SERVERS = {"testing_region":"https://discord.gg/U6DUeVVZpu"}

#These constants are MLSBot responses
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

#The bot secrets are stored in a local .env file for security. No peeking :)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

#Handles a request to get an emoji from a given MLS code
async def handle_get_emoji(message):
    mls = message.content[10:].replace(' gc','').replace(' ','')
    if mls.lower() in MLS_TO_EMOJI:
        await send_msg(message, mls + ' corresponds to ' + MLS_TO_EMOJI[mls.lower()])
    else:
        await send_msg(message, "Unknown MLS abbreviation. You can find valid MLS abbreviations here https://wolfnet.com/market-coverage/.")

#Handles a request to get a discord server link from a given region
async def handle_get_server(message):
    region = message.content[11:].replace(' gc','').replace(' ','')
    if region in REGIONS_TO_SERVERS:
        await send_msg(message, REGIONS_TO_SERVERS[region])
    else:
        await send_msg(message, "Unknown region. Use `!mls regions` to see all valid regions. Use `!mls help` to see other commands.`")

#Handles a request to get the emoji of, region of, and server link of a MLS
#The argument can be either a MLS code or an emoji
async def handle_get_search(message):
    arg = message.content[11:].replace(' gc','').replace(' ','')
    emote = ""
    if arg.lower() in MLS_TO_EMOJI:
        emote = MLS_TO_EMOJI[arg.lower()]
    else:
        emote = arg
    if emote in EMOJI_TO_REGION:
        region = EMOJI_TO_REGION[emote]
        if region in REGIONS_TO_SERVERS:
            await send_msg(message, 'Channel name: ' + emote + ', MLS Region: ' + region)
            await send_msg(message, 'Server link ' + REGIONS_TO_SERVERS[region])
        else:
            await send_msg(message, "It seems we don't have a regional server connected to that valid emoji or MLS code.")
    else: 
        await send_msg(message, "Unknown or MLS code. Use `!mls emoji [valid MLS code]` to find a valid emoji. Find valid MLS abbreviations here https://wolfnet.com/market-coverage/.")

#Handles responding to a command
#By default, the bot direct messages users responses, but adding gc to the end of a request will prompt the bot to respond in the channel the request was made in
async def send_msg(msg_in, msg_out):
    if ('gc' == msg_in.content[-2:]):
        await msg_in.channel.send(msg_out)
    else:
        await msg_in.author.create_dm()
        await msg_in.author.dm_channel.send(msg_out)

#Fires when the bot connects to a serevr it has joined. Exists as a dev-side tool.
@client.event
async def on_ready():
    for guild in client.guilds:
        if (guild.name in GUILD):
            print(f'{client.user} has connected to {guild.name}!')

#The bot always listens for messages, but it only responds when a message begins with !mls
@client.event
async def on_message(message):
    if ('!mls' == message.content[:4]):
        if ('help' == message.content[5:9]):
            await send_msg(message, HELP_TEXT)
        elif ('emoji' == message.content[5:10]):
            await handle_get_emoji(message)
        elif ('regions' == message.content[5:12]):
            await send_msg(message, REGIONS)
        elif ('server' == message.content[5:11]):
            await handle_get_server(message)
        elif ('search' == message.content[5:11]):
            await handle_get_search(message)
        else:
            print(f'Recieved {message.system_content}')
            await message.channel.send("Unknown command. Use `!mls help` to see valid commands.")

#Runs the bot. The rest of this code wouldn't mean much without this line.
client.run(TOKEN)