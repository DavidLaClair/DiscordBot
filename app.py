import configparser
import discord
import logging
import os
from games.games import Games

config_file = "config.ini"

print("Reading config file.")
config = configparser.ConfigParser()
config.read_file(open(config_file))
print("Done reading config file.")

prod = config["General"]["prod"].lower() in ["true", "1"]
if prod:
    print("Starting prod")
    secret = config["General"]["secret"]
    log_name = "prod.log"
else:
    print("Starting dev")
    secret = config["General"]["dev_secret"]
    log_name = "dev.log"

print("Starting logger.")
log_format = "%(asctime)s %(message)s"
logging.basicConfig(filename=log_name, format=log_format, level=logging.INFO, force=True)
logging.info("")
logging.info("Logging initialized.")

logging.info("Initializing Discord Bot.")
client = discord.Client()

games_name = config["Games"]["name"]
games_category_name = config["Games"]["category_name"]
games = Games(None, games_name, games_category_name)

def generate_help():
    help_msg = """Hi {user.mention} I'm here to help!

Here are available commands:
General:
!help                   Gets you this help message!

Games:
!games                  Gives you a list of all available game channels
!join game <name>       Join a specific game channel
!leave game <name>      Leave a specific game channel"""
    return help_msg

async def does_member_have_role(guild, member, role):
    logging.info("'{guild_name}'\t{member}\t{action}".format(guild_name=guild.name, member=member, action="check_role"))
    logging.info("'{guild_name}'\t{member}\t{action}\t{result}".format(guild_name=guild.name, member=member, action="get_member_roles", result=member.roles))

    has_role = False
    #Does user roles match role to add?
    if role in member.roles:
        has_role = True
    
    logging.info("'{guild_name}'\t{member}\t{action}\t{result}".format(guild_name=guild.name, member=member, action="check_role", result=has_role))
    return has_role

async def join_role(guild, member, role):
    logging.info("'{guild_name}'\t{member}\t{action}\t{role_name}".format(guild_name=guild.name, member=member, action="join_role", role_name=role.name))

    #TODO: Add Try/Catch Block
    await member.add_roles(role)

    logging.info("'{guild_name}'\t{member}\t{action}\t{role_name}\t{result}".format(guild_name=guild.name, member=member, action="join_role", role_name=role.name,result="Added to role"))
    
async def leave_role(guild, member, role):
    logging.info("'{guild_name}'\t{member}\t{action}\t{role_name}".format(guild_name=guild.name, member=member, action="leave_role", role_name=role.name))

    #TODO: Add Try/Catch Block
    await member.remove_roles(role)

    logging.info("'{guild_name}'\t{member}\t{action}\t{role_name}\t{result}".format(guild_name=guild.name, member=member, action="leave_role", role_name=role.name,result="Removed from role"))

@client.event
async def on_ready():
    logging.info("'{client}' has connected to Discord.".format(client=client.user))

    games.guild = client.guilds[0]

    #Find and set the category ID(s) for each media type
    games_category_id = discord.utils.get(client.guilds[0].categories, name=games_category_name).id
    games.set_category_id(games_category_id)

    #Populate the channel list for each media type
    games.get_channels()

    #Populate the existing role list for each media type
    games.get_roles()

    #Create any missing roles for each media type
    await games.create_missing_roles()

    ("'{client}' is done initializing and listening!".format(client=client.user))

@client.event
async def on_message(message):
    #Get stuff about the message
    channel = message.channel
    user = message.author
    
    #Ignore messages from self
    if user == client.user:
        return
    
    #DMs should only be requesting help
    if isinstance(channel, discord.channel.DMChannel):
        if message.content == "!help":
            logging.info("{user}\t{action}\t".format(user=user, action="request_help_dm"))
            helpmessage = generate_help()
            await message.author.send(helpmessage.format(user=user))
            return
        else:
            logging.info("{user}\t{action}\t'{message}'".format(user=user, action="invalid_dm_request",message=message.content))
            await message.author.send("Command not supported in DMs.")
            return
    
    #Only listen to the #bot channel from this point on
    if channel.name != "bot":
        return

    #Since the message isn't a DM, get the guild from which the message came
    guild = message.guild

    #Mark the message as processed
    await message.add_reaction("\N{SQUARED OK}")

    #Message a user with available commands
    if message.content == '!help':
        logging.info("'{guild_name}'\t{member}\t{action}".format(guild_name=guild.name, member=user, action="request_help"))
        helpmessage = generate_help()
        await user.send(helpmessage.format(user=user))
        return
    
    #Games
    if message.content == '!games':
        logging.info("'{guild_name}'\t{member}\t{action}".format(guild_name=guild.name, member=user, action="games_list"))
        games_list = games.get_channel_list()
        await channel.send("{user}, here is the current game list:\n{games_list}".format(user=user.mention, games_list=games_list))
        return
    
    #Join a game role
    if message.content.startswith("!join game"):
        game_name = message.content[11:]
        logging.info("'{guild_name}'\t{member}\t{action}\t'{game_name}'".format(guild_name=guild.name, member=user, action="join_game", game_name=game_name))
        role = games.get_role(game_name)

        #Does the role exist?
        if role is None:
            logging.info("'{guild_name}'\t{member}\t{action}\t'{game_name}\t{result}'".format(guild_name=guild.name, member=user, action="join_game", game_name=game_name,result="no_matching_game"))
            await channel.send("{user}, we couldn't find a matching game for '{game_name}'.".format(user=user.mention, game_name=game_name))
            return

        #Is the member already in the role?
        has_role = await does_member_have_role(guild, user, role)
        if has_role:
            logging.info("'{guild_name}'\t{member}\t{action}\t'{game_name}\t{result}'".format(guild_name=guild.name, member=user, action="join_game", game_name=game_name,result="has_role"))
            await channel.send("{user}, you are already a member of {game_name}".format(user=user.mention, game_name=game_name))
            return
        
        await join_role(guild, user, role)
        logging.info("'{guild_name}'\t{member}\t{action}\t'{game_name}\t{result}'".format(guild_name=guild.name, member=user, action="join_game", game_name=game_name, result="added"))
        await channel.send("{user}, you have been added to {game_name}".format(user=user.mention, game_name=game_name))
        return
    
    #Leave a game role
    if message.content.startswith("!leave game"):
        game_name = message.content[12:]
        logging.info("'{guild_name}'\t{member}\t{action}\t'{game_name}'".format(guild_name=guild.name, member=user, action="leave_game", game_name=game_name))
        role = games.get_role(game_name)

        #Does the role exist?
        if role is None:
            logging.info("'{guild_name}'\t{member}\t{action}\t'{game_name}\t{result}'".format(guild_name=guild.name, member=user, action="leave_game", game_name=game_name,result="no_matching_game"))
            await channel.send("{user}, we couldn't find a matching game for '{game_name}'.".format(user=user.mention, game_name=game_name))
            return

        #Is the member part of the role?
        has_role = await does_member_have_role(guild, user, role)
        if not has_role:
            logging.info("'{guild_name}'\t{member}\t{action}\t'{game_name}\t{result}'".format(guild_name=guild.name, member=user, action="leave_game", game_name=game_name,result="doesnt_have_role"))
            await channel.send("{user}, you aren't a member of {game_name}".format(user=user.mention, game_name=game_name))
            return

        await leave_role(guild, user, role)
        logging.info("'{guild_name}'\t{member}\t{action}\t'{game_name}\t{result}'".format(guild_name=guild.name, member=user, action="leave_game", game_name=game_name, result="removed"))
        await channel.send("{user}, you have been removed from {game_name}".format(user=user.mention, game_name=game_name))
        return

logging.info("Starting Discord Bot.")
client.run(secret)