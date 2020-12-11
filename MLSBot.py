#MLSBot.py
"""
@author: Nikhil Devanathan
This script handles the functionality of MLSBot, a discord bot that organizes and helps users of discord servers that host
Multiple Listing Service (MLS) real estate data. Some of the key functionalities of MLSBot are populating regional servers with
appropriate text channels corresponding to different MLSs and helping users navigate the servers and chennels to reach their
desired MLS.
"""
#Default packages
import os
import csv
from collections import defaultdict

#Installed packages
import discord
import emoji
from dotenv import load_dotenv

"""Because MLS codes can get quite cumbersome, channels are named using a combination
of two emojis. The first is a state identifier, and the second distinguishes the MLS.
This bot uses to below dicts to provide a painless interface for users to derive  
emojis from known MLS codes and use emojis to find the correct server."""
MLS_TO_EMOJI = {}
EMOJI_TO_REGION = {}
REGIONS_TO_SERVERS = {}

#These constants are MLSBot responses
HELP_TEXT ="""Hi, I'm MLSBot, and I'm here to help!
Use `!mls` commands to talk to me.
`!mls help` will bring up this text.
Use `!mls emoji [an MLS name]` and I'll give you the two corresponding emojis.
Use `!mls regions` and I'll list out the regions for which we have servers.
Use `!mls server [valid region]` and I'll link you to the appropriate regional server.
Use `!mls search [two emojis or an MLS name]` and I'll link you to the appropriate server.
By default, I'll directly message you any info you request, but if you want it dropped in the text channel, add `here` *to the end* of your command.
Remember, I won't respond to a command that doesn't *start with* `!mls`"""
REGIONS = """The valid regions are:
US Northwest
US Southwest
US Central
US South
US Northeast
US East
US Southeast
Canada"""

#Keys are state abbreviations, values are state names
STATE_SYMBOL_TO_NAME = {}
#Keys are regions, values are a list of state names
REGIONS_TO_STATE = defaultdict(list)
#Keys are states, values are a list of MLS cods
STATE_TO_MLS = defaultdict(list)

#The bot secrets are stored in a local .env file for security. No peeking :)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

#Loads server link data from a csv file. I probably could have pasted it in here, but the csv solution is cleaner.
def load_regional_servers():
    with open('servers.csv') as server_file:
        reader = csv.reader(server_file, delimiter=',')
        for row in reader:
            REGIONS_TO_SERVERS[row[0].strip()] = row[1]

#Loads data regarding the name, symbol, and (arbitrary) region of the 50 US states + 10 Canadian provinces
def load_state_data():
    with open('states.csv') as states_file:
        reader = csv.reader(states_file, delimiter=',')
        for row in reader:
            REGIONS_TO_STATE[row[2].strip()].append(row[0])
            STATE_SYMBOL_TO_NAME[row[1].lower()] = row[0]

#Loads the data corresponding mls codes and emojis from mls.csv. The first two letters of each mls code are a state symbol
def load_mls_data():
    with open('mls.csv', encoding='utf-8') as mls_file:
        reader = csv.reader(mls_file, delimiter=',')
        for row in reader:
            MLS_TO_EMOJI[row[2]] = row[3]
            symbol = row[2][:2]
            state = STATE_SYMBOL_TO_NAME[symbol]
            STATE_TO_MLS[state].append(row[2])
            for region in REGIONS_TO_STATE:
                if state in REGIONS_TO_STATE[region]:
                    EMOJI_TO_REGION[row[3]] = region

#Handles a request to get an emoji from a given MLS code
async def handle_get_emoji(message):
    mls = message.content[5:].strip()[5:].strip().lower().replace(' here','').replace(' ','')
    if mls.lower() in MLS_TO_EMOJI:
        await send_msg(message, mls + ' corresponds to ' + MLS_TO_EMOJI[mls.lower()])
    else:
        await send_msg(message, "Unknown MLS abbreviation. You can find valid MLS abbreviations here https://wolfnet.com/market-coverage/.")

#Handles a request to get a discord server link from a given region
async def handle_get_server(message):
    region = message.content[5:].strip()[6:].strip().lower().replace(' here','').strip().title()
    if region.lower() in REGIONS_TO_SERVERS:
        await send_msg(message, 'Server link: ' + REGIONS_TO_SERVERS[region])
    else:
        await send_msg(message, "Unknown region. Use `!mls regions` to see all valid regions. Use `!mls help` to see other commands.")

#Handles a request to get the emoji of, region of, and server link of a MLS
#The argument can be either a MLS code or an emoji
async def handle_get_search(message):
    arg = message.content[5:].strip()[6:].strip().lower().replace(' here','').replace(' ','')
    emote = ""
    if arg.lower() in MLS_TO_EMOJI:
        emote = MLS_TO_EMOJI[arg.lower()]
    else:
        emote = arg
    if emote in EMOJI_TO_REGION:
        region = EMOJI_TO_REGION[emote]
        if region in REGIONS_TO_SERVERS:
            await send_msg(message, 'Channel name: ' + emote + ', MLS Region: ' + region)
            await send_msg(message, 'Server link: ' + REGIONS_TO_SERVERS[region])
        else:
            await send_msg(message, "It seems we don't have a regional server connected to that valid emoji or MLS code.")
    else: 
        await send_msg(message, "Unknown emoji or MLS code. Use `!mls emoji [valid MLS code]` to find a valid emoji. Find valid MLS abbreviations here https://wolfnet.com/market-coverage/.")

#A wrapper function for populate server that ensures the command was sent in a server channel and that the sender is a server admin
async def handle_populate(message):
    if (message.guild):
        if (message.author.permissions_in(message.channel).administrator):
            await populate_server(message)
        else:
            return
    else:
        return

#Handles responding to a command
#By default, the bot direct messages users responses, but adding 'here' to the end of a request will prompt the bot to respond in the channel the request was made in
async def send_msg(msg_in, msg_out):
    if ('here' == msg_in.content[-4:].lower()):
        await msg_in.channel.send(msg_out)
    else:
        await msg_in.author.create_dm()
        await msg_in.author.dm_channel.send(msg_out)

#Adds general channels to a server and calls populate_mls_channels to fill each state category with relevant channels
async def populate_server(message):
    guild_name = message.guild.name
    if ('-' in guild_name) and (guild_name.index('-') + 1 < len(guild_name)):
        region = guild_name[guild_name.index('-')+1:]
        general = await message.guild.create_category('General')
        await general.create_text_channel('Rules')
        await general.create_text_channel('Announcements')
        await general.create_text_channel('Welcome')
        await general.create_text_channel('General')
        await general.create_text_channel('Q/A')
        await general.create_text_channel('Bot')
        await general.create_voice_channel('Admin Voice Room')
        await general.create_voice_channel('Voice Room 1')
        await general.create_voice_channel('Voice Room 2')
        for state in REGIONS_TO_STATE[region.strip()]:
            cat = await message.guild.create_category(state)
            await populate_mls_channels(cat)

#Adds mls channels named after emojis to every state category
async def populate_mls_channels(cat):
    mls_codes = STATE_TO_MLS[cat.name]
    await cat.create_text_channel(cat.name + '-general')
    await cat.create_text_channel(cat.name + '-bot')
    await cat.create_voice_channel(cat.name + '-general')
    for code in mls_codes:
        emoji = MLS_TO_EMOJI[code]
        await cat.create_text_channel(emoji)

#Fires when the bot connects to a serevr it has joined. Exists as a dev-side tool.
@client.event
async def on_ready():
    for guild in client.guilds:
        print(f'{client.user} has connected to {guild.name}!')

#The bot always listens for messages, but it only responds when a message begins with !mls
@client.event
async def on_message(message):
    if ('!mls' == message.content[:4].lower()):
        if ('help' == message.content[5:].strip()[:4].lower()):
            await send_msg(message, HELP_TEXT)
        elif ('emoji' == message.content[5:].strip()[:5].lower()):
            await handle_get_emoji(message)
        elif ('regions' == message.content[5:].strip()[:7].lower()):
            await send_msg(message, REGIONS)
        elif ('server' == message.content[5:].strip()[:6].lower()):
            await handle_get_server(message)
        elif ('search' == message.content[5:].strip()[:6].lower()):
            await handle_get_search(message)
        elif ('populate' == message.content[5:].strip()[:8].lower()):
            await handle_populate(message)
        else:
            print(f'Recieved {message.system_content}')
            await message.channel.send("Unknown command. Use `!mls help` to see valid commands.")

#Populate the global dicts with data from input files
load_regional_servers()
load_state_data()
load_mls_data()

#Runs the bot. The rest of this code wouldn't mean much without this line.
client.run(TOKEN)