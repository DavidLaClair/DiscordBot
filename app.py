import configparser
import discord
import os
from games.games import Games

config_file = "config.ini"

print("Reading Config file")
config = configparser.ConfigParser()
config.read_file(open(config_file))

print("Initializing Discord Bot")
client = discord.Client()

games_name = config["Games"]["name"]
games_category_name = config["Games"]["category_name"]
games = Games(games_name, games_category_name)


async def userToMember(user):
    print("We are trying to convert {user} to a member.".format(user=user))
    member = discord.utils.get(client.guilds[0].members, name=user.name)

    print("Here's the result of converting {user} to a member: {member}".format(user=user, member=member))
    return member

async def does_member_have_role(member, role):
    print("We are checking if '{member}' has role '{role}'".format(member=member, role=role))

    #Get user roles
    print("Member roles:")
    print(member.roles)

    #Does user roles match role to add?
    #Return true if yes, false if no
    if role in member.roles:
        print("They have the role!")
        return True
    
    print("They do not have the role!")
    return False

async def join_role(member, role):
    print("We are adding {member} to '{role}'.".format(member=member, role=role))

    await member.add_roles(role)
    print("Added {member} to '{role}'".format(member=member.name, role=role))
    
async def leave_role(member, role):
    print("We are removing {member} from '{role}'.".format(member=member, role=role))

    await member.remove_roles(role)
    print("Removed {member} from '{role}'".format(member=member.name, role=role))

@client.event
async def on_ready():
    print("{client} has connect to Discord! Beginning initialization".format(client=client.user))

    #Find and set the category ID(s) for each media type
    games_category_id = discord.utils.get(client.guilds[0].categories, name=games_category_name).id
    games.set_category_id(games_category_id)

    #Populate the channel list for each media type
    games.get_channels(client.guilds[0])

    #Populate the existing role list for each media type
    games.get_roles(client.guilds[0])

    #Create any missing roles for each media type
    games.create_missing_roles(client.guilds[0])

    print("Done with initialization!")
    print()
    print()

@client.event
async def on_message(message):
    #Get stuff about the message
    channel = message.channel
    user = message.author
    
    #Ignore messages from self
    if user == client.user:
        return
    
    #Only listen to the bot channel for help
    if not isinstance(channel, discord.channel.DMChannel):
        if channel.name == "bot" and message.content == '!help':
            print("{user} has requested help.".format(user=user))
            helpmessage = config["General"]["helpmessage"]
            await message.author.send(helpmessage.format(user=user))
            await message.delete()
        elif channel.name == "bot":
            await message.author.send("Please only use '!help' in the bot channel.")
            await message.delete()

    #From this point on, only allow DMs
    if not isinstance(channel, discord.channel.DMChannel):
        return

    #Seperate log messages
    print()

    #Message a user with available commands
    if message.content == '!help':
        print("{user} has requested help.".format(user=user))
        helpmessage = config["General"]["helpmessage"]
        await user.send(helpmessage.format(user=user))
    
    #Games
    if message.content == '!games':
        games_list = games.get_channel_list()
        await user.send("Here is the current game list:\n" + games_list)
    
    #Join a game role
    if message.content.startswith("!join game"):
        game_name = message.content[11:]
        print("'{user}' has requested to join game channel for '{game_name}'".format(user=user.name, game_name=game_name))
        member = await userToMember(user)
        role = games.get_role(game_name)

        #Is the user a member of the server?
        if member is None:
            print("User membership not found.")
            await user.send("We could find your membership to a server!")
            return

        #Does the role exist?
        if role is None:
            print("Game not found.")
            await user.send("We could find a matching game!")
            return

        #Is the member already in the role?
        has_role = await does_member_have_role(member, role)
        if has_role:
            print("User already has role.")
            await user.send("You are already a member of {game_name}".format(game_name=game_name))
            return
        
        await join_role(member, role)
        await user.send("You have been added to {game_name}!".format(game_name=game_name))
    
    #Leave a game role
    if message.content.startswith("!leave game"):
        game_name = message.content[12:]
        print("'{user}' has requested to leave game channel for '{game_name}'".format(user=user.name, game_name=game_name))
        member = await userToMember(user)
        role = games.get_role(game_name)

        #Is the user a member of the server?
        if member is None:
            print("User membership not found.")
            await user.send("We could find your membership to a server!")
            return

        #Does the role exist?
        if role is None:
            print("Game not found.")
            await user.send("We could find a matching game!")
            return

        #Is the member part of the role?
        has_role = await does_member_have_role(member, role)
        if not has_role:
            print("User doesn't have role.")
            await user.send("You aren't a member of {game_name}".format(game_name=game_name))
            return

        await leave_role(member, role)
        await user.send("You have been removed from {game_name}!".format(game_name=game_name))

print("Starting Discord Bot")
client.run(config["General"]["secret"])