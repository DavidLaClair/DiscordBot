import os
import discord

print("Initializing Discord Bot")
client = discord.Client()

games_category_name = "Games"
game_channel_approver_role_name = "Game Approver"
games_channels = {}
games_roles = {}

helpmessage = """
Hi {user.mention} I'm here to help!
Please use all commands here in our DM.

Here are available commands:
General:
!help                   Gets you this help message!

Games:
!games                  Gives you a list of all available game channels
!join game <name>       Join a specific game channel
!leave game <name>      Leave a specific game channel
"""

async def populate_categories():
    print("Updating category list.")
    
    #Get Games Category ID
    games_category_id = discord.utils.get(client.guilds[0].categories, name=games_category_name).id

    for channel in client.guilds[0].channels:
        #Populate game category
        if channel.category_id == games_category_id:
            games_channels[channel.name] = channel
    
    print("Found the following game channels:")
    print(games_channels)

async def get_games_list():
    val = ""

    for key in games_channels:
        val += key + "\n"
    
    return val

async def get_role(role_type, name):
    print("We are looking for a role called {role_type}-{name}".format(role_type=role_type, name=name))
    #Update roles before searching
    await get_existing_roles()

    role = None

    if role_type == "game":
        if name in games_roles:
            role = games_roles[name]

    print("Here's the role we are returning: {role}".format(role=role))
    return role

async def get_existing_roles():
    print("Updating current roles.")

    for role in client.guilds[0].roles:
        if role.name.startswith("game-"):
            game_name = role.name[5:]
            games_roles[game_name] = role
    
    print("We found the following game roles:")
    print(games_roles)

async def create_role(role_type, game_name):
    role_name = role_type + "-" + game_name
    print("Creating role {role}".format(role=role_name))
    
    #Create role
    role = await client.guilds[0].create_role(name=role_name)

    #add to games_roles DB
    games_roles[game_name] = role

    #return the new role
    return role

async def create_missing_roles():
    print("We are looking for roles we need to create.")
    for game in games_channels:
        if game not in games_roles:
            new_role = await create_role("game", game)

            await (games_channels[game]).set_permissions(new_role, read_messages=True, send_messages=True, read_message_history=True)

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

async def join_role(user, role_type, name):
    print("{user} has requested to join {role_type}-{name}.".format(user=user, role_type=role_type, name=name))

    #Prepare everything we need to join the role
    role_to_add = await get_role(role_type, name)
    member = await userToMember(user)

    #Is the user a member of the server?
    if member is None:
        print("User membership not found.")
        await user.send("We could find your membership to a server!")
        return

    #We couldn't find the role, tell the user and do nothing
    if role_to_add is None:
        print("Role not found.")
        await user.send("We couldn't find a matching {role_type} for '{name}'".format(role_type=role_type, name=name))
        return

    #Check if they already have the role, tell the user and do nothing if they do
    has_role = await does_member_have_role(member, role_to_add)
    if has_role:
        await user.send("You are already a member of that {role_type}!".format(role_type=role_type))
        return

    #Finally, add them to the role
    print("Adding {user} to {role_type}-{name}".format(user=member.name, role_type=role_type, name=name))
    await member.add_roles(role_to_add)
    await user.send("You have been added to the {role_type}!".format(role_type=role_type))

async def leave_role(user, role_type, name):
    print("{user} has requested to leave {role_type}-{name}.".format(user=user, role_type=role_type, name=name))

    #prepare everything we need to leave the role
    role_to_remove = await get_role(role_type, name)
    member = await userToMember(user)

    #Is the user a member of the server?
    if member is None:
        print("User membership not found.")
        await user.send("We could find your membership to a server!")
        return
    
    #We couldn't find the role, tell the user and do nothing
    if role_to_remove is None:
        print("Role not found.")
        await user.send("We couldn't find a matching {role_type} for '{name}'".format(role_type=role_type, name=name))
        return
    
    #Check if the member has the role, tell the user and do nothing if they don't
    has_role = await does_member_have_role(member, role_to_remove)
    if not has_role:
        await user.send("You aren't a member of that {role_type}!".format(role_type=role_type))
        return
    
    #Finally, remove the role
    print("Removing {user} from {role_type}-{name}".format(user=member.name, role_type=role_type, name=name))
    await member.remove_roles(role_to_remove)
    await user.send("You have been removed from the {role_type}!".format(role_type=role_type))

@client.event
async def on_ready():
    print(f'{client.user} has connect to Discord')

    print("Categories:")
    await populate_categories()

    print("Managed Roles:")
    await get_existing_roles()
    await create_missing_roles()

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
            print("Helping {user}".format(user=user))
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
        await user.send(helpmessage.format(user=user))
    
    #Games
    if message.content == '!games':
        games_list = await get_games_list()
        await user.send("Here is the current game list:\n" + games_list)
    
    #Join a game role
    if message.content.startswith("!join game"):
        game_to_join = message.content[11:]
        await join_role(user, "game", game_to_join)
    
    #Leave a game role
    if message.content.startswith("!leave game"):
        game_to_leave = message.content[12:]
        await leave_role(user, "game", game_to_leave)

print("Starting Discord Bot")
client.run('Mjk1ODk4NjY2Mzk1MjM4NDEw.WNkHGw.GXV8J8bh0XMk63Wv2VC8R7W-bSE')